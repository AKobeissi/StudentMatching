from fastapi import FastAPI, UploadFile, File, HTTPException
from gurobipy import Model, GRB
import pandas as pd
import io
from pre_process import preprocess_data  

app = FastAPI()


@app.post("/optimize")
async def optimize(student_file: UploadFile = File(...), host_file: UploadFile = File(...)):
    try:
        # Preprocess the uploaded files
        students_clean, hosts_clean = preprocess_data(student_file, host_file)
        
        # Define time slots
        time_slots = [
            "23 décembre AM", "23 décembre PM", "24 décembre AM", "24 décembre PM",
            "25 décembre AM", "25 décembre PM", "26 décembre AM", "26 décembre PM",
            "27 décembre AM", "27 décembre PM", "28 décembre AM", "28 décembre PM",
            "29 décembre AM", "29 décembre PM", "30 décembre AM", "30 décembre PM",
            "31 décembre AM", "31 décembre PM", "1er janvier AM", "1er janvier PM",
            "2 janvier AM", "2 janvier PM", "3 janvier AM", "3 janvier PM"
        ]

        # Build Compatibility Matrix
        c = {}
        for _, student in students_clean.iterrows():
            for _, host in hosts_clean.iterrows():
                for time in time_slots:
                    # Default compatibility score
                    score = 0

                    # Check basic availability
                    if time in student['preferred_dates'] and time in host['preferred_dates']:
                        # Language similarity
                        language_score = 2 if any(lang in host['languages_spoken'] for lang in student['languages_spoken']) else 1

                        # Activity compatibility
                        activity_score = 2 if any(activity in host['offered_activities'] for activity in student['preferred_activities']) else 1
                                    
                        # Calculate final score for this time slot
                        score = 0.5 * language_score + 0.5 * activity_score 
                                
                    # Store the time-specific compatibility score
                    c[(student['student_id'], host['host_id'], time)] = score

        # Generate aggregated compatibility matrix for output
        aggregated_c = {}
        for (s, h, t), score in c.items():
            if (s, h) not in aggregated_c:
                aggregated_c[(s, h)] = 0
            aggregated_c[(s, h)] += score

        # Save the aggregated compatibility matrix to a CSV file
        aggregated_c_df = pd.DataFrame([
            {"Student_ID": s, "Host_ID": h, "Compatibility": score}
            for (s, h), score in aggregated_c.items()
        ])
        #aggregated_c_df.to_csv("aggregated_compatibility_matrix.csv", index=False)

        # Initialize Gurobi Model
        model = Model("Student-Host Matching")
        x = model.addVars(
            students_clean['student_id'],
            hosts_clean['host_id'],
            time_slots,
            vtype=GRB.BINARY,
            name="x"
        )
        e = model.addVars(hosts_clean['host_id'], time_slots, vtype=GRB.BINARY, name="e")

        # Objective Function
        model.setObjective(
            sum(c[s, h, t] * x[s, h, t] * e[h, t] for s in students_clean['student_id'] for h in hosts_clean['host_id'] for t in time_slots),
            GRB.MAXIMIZE
        )

        # Constraints
        # 1. Each student assigned to at most one host at one time
        for s in students_clean['student_id']:
            model.addConstr(
                sum(x[s, h, t] for h in hosts_clean['host_id'] for t in time_slots) <= 1
            )

        # 2. Each host organizes at most one event per time slot
        for h in hosts_clean['host_id']:
            model.addConstr(sum(e[h, t] for t in time_slots) <= 1)

        # 3. Hosting events must have between 2 and the host's capacity
        for h, host in hosts_clean.iterrows():
            for t in time_slots:
                model.addConstr(
                    2 * e[host['host_id'], t] <= sum(x[s, host['host_id'], t] for s in students_clean['student_id'])
                )
                model.addConstr(
                    sum(x[s, host['host_id'], t] for s in students_clean['student_id']) <= host['num_students'] * e[host['host_id'], t]
                )

        for _, student in students_clean.iterrows():
            for _, host in hosts_clean.iterrows():
                for t in time_slots:
                    # Language compatibility
                    if set(student["language"]) == {"English (United States)"} and host['comfortable_in_english'] == "Non":
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)

                    # Dietary restrictions
                    if set(student['dietary_restrictions']) != {"Non"} and host['food_restriction_commitment'] != "Oui":
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)

                    # Pet restrictions
                    if not "Non" in student['pet_allergies'] and any(pet in host['pets_at_home'] for pet in student['pet_allergies']):
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)

                    # Gender preferences
                    #host-level
                    if host['woman_group_preference'] == "Oui" and student['gender'] != "Femme":
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)
                    if host["gender"] != "Femme" and student["woman_group_preference"] == "Oui":
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)
                    #student-level
                    if student["woman_group_preference"] == "Oui":
                        for _, other_student in students_clean.iterrows():
                            if other_student['gender'] != "Femme":
                                model.addConstr(
                                    x[other_student['student_id'], host['host_id'], t] + x[student['student_id'], host['host_id'], t] <= 1
                                )

        # 4. Availability constraints
        for _, student in students_clean.iterrows():
            for _, host in hosts_clean.iterrows():
                for t in time_slots:
                    if t not in student['preferred_dates'] or t not in host['preferred_dates']:
                        model.addConstr(x[student['student_id'], host['host_id'], t] == 0)

        # Solve Model
        model.optimize()

        # Output Results

        # Collect results
        if model.status == GRB.OPTIMAL:
            assignments = [
                {"student_id": s, "host_id": h, "time_slot": t}
                for s in students_clean['student_id']
                for h in hosts_clean['host_id']
                for t in time_slots
                if x[s, h, t].X > 0.5
            ]

            return {"status": "success", "assignments": assignments}
        else:
            return {"status": "failure", "message": "No optimal solution found"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
