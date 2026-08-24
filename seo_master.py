import os
import sys
import json
import argparse
from datetime import datetime

STATE_FILE = "seo_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        alt_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STATE_FILE)
        if os.path.exists(alt_path):
            with open(alt_path, 'r') as f:
                return json.load(f)
        print(f"Error: {STATE_FILE} not found. Ensure you are running from the workspace root or directory containing it.")
        sys.exit(1)
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_workspace_root():
    # Find where seo_state.json resides
    curr = os.path.abspath(os.getcwd())
    while True:
        if os.path.exists(os.path.join(curr, STATE_FILE)):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.getcwd())

def get_local_session_path():
    cwd = os.path.abspath(os.getcwd())
    root = get_workspace_root()
    
    # Traverse from CWD up to root looking for .session.json
    curr = cwd
    while True:
        sess_file = os.path.join(curr, ".session.json")
        if os.path.exists(sess_file):
            return sess_file
        if curr == root:
            break
        curr = os.path.dirname(curr)
        
    # If not found, default to writing in CWD
    return os.path.join(cwd, ".session.json")

def load_local_session():
    path = get_local_session_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_local_session(session_data):
    path = get_local_session_path()
    with open(path, 'w') as f:
        json.dump(session_data, f, indent=2)

def get_current_user(state):
    sess = load_local_session()
    return sess.get("current_user")

def get_user_info(state, username):
    return state.get("users", {}).get(username)

def log_activity(state, user, sub_project, project, task_id, agent, action, result):
    activity = {
        "user": user,
        "sub_project": sub_project,
        "project": project,
        "task_id": task_id,
        "agent": agent,
        "action": action,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    state["activity_log"].append(activity)
    
    if sub_project:
        root = get_workspace_root()
        local_dir = os.path.join(root, "subprojects", sub_project.lower())
        if os.path.exists(local_dir):
            local_log_path = os.path.join(local_dir, "activity.jsonl")
            try:
                with open(local_log_path, 'a') as f:
                    f.write(json.dumps(activity) + "\n")
            except Exception:
                pass

def check_permission(state, permission_name):
    curr_user = get_current_user(state)
    if not curr_user:
        return False, "No active session. Please run START to log in."
    
    user_info = get_user_info(state, curr_user)
    if not user_info:
        return False, f"User '{curr_user}' not found in configuration."
        
    role = user_info.get("role")
    permissions = user_info.get("permissions", [])
    
    if role == "ADMIN":
        return True, None
    if permission_name in permissions:
        return True, None
        
    return False, f"Permission Denied: User '{curr_user}' (Role: {role}) does not have permission '{permission_name}'."

def cmd_start(args):
    state = load_state()
    username = args.name.strip()
    username = username.capitalize()
    
    user_info = get_user_info(state, username)
    if not user_info:
        print(f"Error: User '{username}' is not a permanent team member. Authorized members: Dived, Chirag, Ravi, Prashant, Kanishak.")
        sys.exit(1)
        
    # Write to local session file
    session_data = {
        "current_user": username,
        "viewing_subproject": username
    }
    save_local_session(session_data)
    
    role = user_info.get("role")
    perms = user_info.get("permissions", [])
    
    print(f"Welcome {username}.")
    print(f"Role: {role.replace('_', ' ').title()}")
    print(f"Sub-project: {username}")
    print("Available SEO functions:")
    
    perm_map = {
        "on_page": "1. On-Page & Content",
        "off_page": "2. Off-Page & Authority",
        "technical": "3. Technical SEO",
        "research": "4. SEO Research & R&D",
        "intelligence": "5. SEO Intelligence & Analytics",
        "testing": "6. SEO Testing & QA",
        "strategy": "7. Full SEO Strategy",
        "projects": "8. Projects Management",
        "team_management": "9. Team Management",
        "reports": "10. Reports"
    }
    
    if role == "ADMIN":
        for val in perm_map.values():
            print(f"- {val}")
    else:
        for p in perms:
            if p in perm_map:
                print(f"- {perm_map[p]}")
                
    active_tasks = [t for tid, t in state["tasks"].items() if t["owner"] == username and t["status"] in ["ASSIGNED", "IN_PROGRESS", "NEEDS_REVISION"]]
    if active_tasks:
        print("\nYour Active Tasks:")
        for t in active_tasks:
            print(f"  - [{t['id']}] {t['name']} (Project: {t['project']}) | Status: {t['status']}")
            
    print("\nWhat would you like to work on?")
    
    log_activity(state, username, username, None, None, None, "START (Login)", "SUCCESS")
    save_state(state)

def cmd_session(args):
    state = load_state()
    sess = load_local_session()
    curr_user = sess.get("current_user")
    if not curr_user:
        print("No active session. Please start a session with the START command.")
        sys.exit(1)
        
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    viewing = sess.get("viewing_subproject", curr_user)
    
    print(f"Current Session User: {curr_user}")
    print(f"Role: {role}")
    print(f"Currently Viewing Workspace/Sub-project: {viewing}")
    print(f"Permissions: {', '.join(user_info.get('permissions', []))}")

def cmd_logout(args):
    state = load_state()
    sess = load_local_session()
    curr_user = sess.get("current_user")
    if not curr_user:
        print("No active session to stop.")
        sys.exit(1)
        
    path = get_local_session_path()
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass
            
    print(f"Session stopped. Logged out user '{curr_user}'.")
    log_activity(state, curr_user, curr_user, None, None, None, "STOP (Logout)", "SUCCESS")
    save_state(state)

def cmd_users(args):
    state = load_state()
    ok, err = check_permission(state, "team_management")
    if not ok:
        print(err)
        sys.exit(1)
        
    print("| User | Role | Permissions |")
    print("| --- | --- | --- |")
    for username, info in state["users"].items():
        print(f"| {username} | {info['role']} | {', '.join(info['permissions'])} |")

def cmd_grant(args):
    state = load_state()
    ok, err = check_permission(state, "team_management")
    if not ok:
        print(err)
        sys.exit(1)
        
    username = args.name.capitalize()
    permission = args.permission.strip().lower()
    
    user_info = get_user_info(state, username)
    if not user_info:
        print(f"Error: User '{username}' not found.")
        sys.exit(1)
        
    valid_perms = ["on_page", "off_page", "technical", "research", "intelligence", "testing", "strategy", "projects", "team_management", "reports"]
    if permission not in valid_perms:
        print(f"Error: Invalid permission '{permission}'. Choose from: {', '.join(valid_perms)}")
        sys.exit(1)
        
    if permission in user_info["permissions"]:
        print(f"User '{username}' already has permission '{permission}'.")
        return
        
    user_info["permissions"].append(permission)
    print(f"Granted '{permission}' permission to '{username}'.")
    
    curr_user = get_current_user(state)
    log_activity(state, curr_user, curr_user, None, None, None, f"Grant Permission {permission} to {username}", "SUCCESS")
    save_state(state)

def cmd_revoke(args):
    state = load_state()
    ok, err = check_permission(state, "team_management")
    if not ok:
        print(err)
        sys.exit(1)
        
    username = args.name.capitalize()
    permission = args.permission.strip().lower()
    
    user_info = get_user_info(state, username)
    if not user_info:
        print(f"Error: User '{username}' not found.")
        sys.exit(1)
        
    if permission not in user_info["permissions"]:
        print(f"User '{username}' does not have permission '{permission}'.")
        sys.exit(1)
        
    user_info["permissions"].remove(permission)
    print(f"Revoked '{permission}' permission from '{username}'.")
    
    curr_user = get_current_user(state)
    log_activity(state, curr_user, curr_user, None, None, None, f"Revoke Permission {permission} from {username}", "SUCCESS")
    save_state(state)

def cmd_create_project(args):
    state = load_state()
    ok, err = check_permission(state, "projects")
    if not ok:
        print(err)
        sys.exit(1)
        
    proj_name = args.name.strip()
    proj_desc = args.description.strip()
    
    if proj_name in state["projects"]:
        print(f"Error: Project '{proj_name}' already exists.")
        sys.exit(1)
        
    curr_user = get_current_user(state)
    state["projects"][proj_name] = {
        "description": proj_desc,
        "created_by": curr_user,
        "created_at": datetime.now().isoformat()
    }
    
    print(f"Project '{proj_name}' created successfully.")
    log_activity(state, curr_user, curr_user, proj_name, None, None, "Create Project", "SUCCESS")
    save_state(state)

def cmd_list_projects(args):
    state = load_state()
    if not state["projects"]:
        print("No projects exist yet.")
        return
        
    print("| Project Name | Description | Created By | Created At |")
    print("| --- | --- | --- | --- |")
    for name, info in state["projects"].items():
        print(f"| {name} | {info['description']} | {info['created_by']} | {info['created_at'][:10]} |")

def cmd_create_task(args):
    state = load_state()
    ok, err = check_permission(state, "projects")
    if not ok:
        print(err)
        sys.exit(1)
        
    proj_name = args.project.strip()
    if proj_name not in state["projects"]:
        print(f"Error: Project '{proj_name}' does not exist. Create the project first.")
        sys.exit(1)
        
    owner = args.owner.capitalize()
    if owner not in state["users"]:
        print(f"Error: Owner '{owner}' is not a valid team member.")
        sys.exit(1)
        
    agent = args.agent.upper()
    valid_agents = ["ON-PAGE & CONTENT", "OFF-PAGE & AUTHORITY", "TECHNICAL SEO", "SEO RESEARCH & R&D", "SEO INTELLIGENCE & ANALYTICS", "SEO TESTING & QA"]
    if agent not in valid_agents:
        print(f"Error: Invalid agent '{agent}'. Valid agents: {', '.join(valid_agents)}")
        sys.exit(1)
        
    task_name = args.name.strip()
    objective = args.objective.strip()
    priority = args.priority.upper() if args.priority else "MEDIUM"
    
    collaborators = [c.strip().capitalize() for c in args.collaborators.split(",")] if args.collaborators else []
    dependencies = [d.strip() for d in args.dependencies.split(",")] if args.dependencies else []
    
    task_id = f"TSK-{len(state['tasks']) + 1:03d}"
    
    state["tasks"][task_id] = {
        "id": task_id,
        "name": task_name,
        "project": proj_name,
        "subproject": owner,
        "owner": owner,
        "collaborators": collaborators,
        "seo_agent": agent,
        "objective": objective,
        "priority": priority,
        "status": "ASSIGNED",
        "work_performed": "",
        "findings": [],
        "evidence": "",
        "deliverable": "",
        "qa_status": "PENDING",
        "qa_feedback": "",
        "dependencies": dependencies,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    print(f"Task '{task_id}' created and assigned to {owner} (Sub-project: {owner}).")
    curr_user = get_current_user(state)
    log_activity(state, curr_user, curr_user, proj_name, task_id, agent, f"Create Task assigned to {owner}", "SUCCESS")
    save_state(state)

def cmd_list_tasks(args):
    state = load_state()
    sess = load_local_session()
    curr_user = sess.get("current_user")
    if not curr_user:
        print("No active session. Please START session first.")
        sys.exit(1)
        
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    viewing = sess.get("viewing_subproject", curr_user)
    
    tasks = state["tasks"]
    filtered = []
    
    for tid, t in tasks.items():
        if args.owner and t["owner"].lower() != args.owner.lower():
            continue
        if args.project and t["project"].lower() != args.project.lower():
            continue
        if args.status and t["status"].lower() != args.status.lower():
            continue
            
        if role != "ADMIN":
            if t["subproject"] != curr_user and t["owner"] != curr_user and curr_user not in t["collaborators"]:
                continue
        else:
            if viewing and viewing != curr_user and not args.owner and not args.all:
                if t["subproject"] != viewing:
                    continue
                    
        filtered.append(t)
        
    if not filtered:
        print("No tasks found matching criteria.")
        return
        
    print("| Task ID | Name | Project | Owner | Sub-project | Agent | Status | Priority | QA |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for t in filtered:
        print(f"| {t['id']} | {t['name']} | {t['project']} | {t['owner']} | {t['subproject']} | {t['seo_agent']} | {t['status']} | {t['priority']} | {t['qa_status']} |")

def cmd_update_task(args):
    state = load_state()
    curr_user = get_current_user(state)
    if not curr_user:
        print("No active session.")
        sys.exit(1)
        
    task_id = args.id.strip().upper()
    if task_id not in state["tasks"]:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)
        
    task = state["tasks"][task_id]
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    
    if role != "ADMIN" and task["owner"] != curr_user and curr_user not in task["collaborators"]:
        print(f"Error: You do not have permission to edit Task '{task_id}'. Owner is {task['owner']}.")
        sys.exit(1)
        
    updated = False
    
    if args.status:
        new_status = args.status.upper().replace("_", " ")
        valid_statuses = ["BACKLOG", "ASSIGNED", "IN PROGRESS", "BLOCKED", "SUBMITTED FOR QA", "NEEDS REVISION", "QA PASSED", "COMPLETED"]
        if new_status not in valid_statuses:
            print(f"Error: Invalid status '{new_status}'.")
            sys.exit(1)
        task["status"] = new_status
        updated = True
        
    if args.work:
        task["work_performed"] = args.work.strip()
        updated = True
        
    if args.findings:
        task["findings"] = [f.strip() for f in args.findings.split(";;")]
        updated = True
        
    if args.evidence:
        task["evidence"] = args.evidence.strip()
        updated = True
        
    if args.deliverable:
        task["deliverable"] = args.deliverable.strip()
        updated = True
        
    if args.owner:
        ok, err = check_permission(state, "projects")
        if not ok:
            print(err)
            sys.exit(1)
        new_owner = args.owner.capitalize()
        if new_owner not in state["users"]:
            print(f"Error: User '{new_owner}' is not a valid team member.")
            sys.exit(1)
        task["owner"] = new_owner
        task["subproject"] = new_owner
        updated = True
        print(f"Task '{task_id}' reassigned to {new_owner}.")
        
    if updated:
        task["updated_at"] = datetime.now().isoformat()
        print(f"Task '{task_id}' updated successfully.")
        log_activity(state, curr_user, task["subproject"], task["project"], task_id, task["seo_agent"], "Update Task", "SUCCESS")
        save_state(state)
    else:
        print("No updates specified.")

def cmd_submit(args):
    state = load_state()
    curr_user = get_current_user(state)
    if not curr_user:
        print("No active session.")
        sys.exit(1)
        
    task_id = args.id.strip().upper()
    if task_id not in state["tasks"]:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)
        
    task = state["tasks"][task_id]
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    
    if role != "ADMIN" and task["owner"] != curr_user:
        print(f"Error: Only the owner ({task['owner']}) can submit Task '{task_id}' for QA.")
        sys.exit(1)
        
    if not task["work_performed"] and not task["deliverable"]:
        print("Error: Cannot submit task for QA without documenting work performed or findings.")
        sys.exit(1)
        
    task["status"] = "SUBMITTED FOR QA"
    task["qa_status"] = "PENDING"
    task["updated_at"] = datetime.now().isoformat()
    
    print(f"Task '{task_id}' has been submitted for QA Testing.")
    log_activity(state, curr_user, task["subproject"], task["project"], task_id, task["seo_agent"], "Submit Task for QA", "SUCCESS")
    save_state(state)

def cmd_test(args):
    state = load_state()
    ok, err = check_permission(state, "testing")
    if not ok:
        print(err)
        sys.exit(1)
        
    task_id = args.id.strip().upper()
    if task_id not in state["tasks"]:
        print(f"Error: Task '{task_id}' not found.")
        sys.exit(1)
        
    task = state["tasks"][task_id]
    result = args.result.upper().replace("_", " ")
    valid_results = ["PASS", "FAIL", "NEEDS REVISION", "BLOCKED", "NOT VERIFIABLE"]
    if result not in valid_results:
        print(f"Error: Invalid QA result '{result}'. Valid: {', '.join(valid_results)}")
        sys.exit(1)
        
    feedback = args.feedback.strip() if args.feedback else ""
    task["qa_status"] = result
    task["qa_feedback"] = feedback
    
    curr_user = get_current_user(state)
    
    if result == "PASS":
        task["status"] = "COMPLETED"
        print(f"QA PASSED: Task '{task_id}' is approved and marked as COMPLETED.")
        
        if task["findings"] or task["deliverable"]:
            content = f"### Deliverable: {task['name']}\nProject: {task['project']}\nOwner: {task['owner']}\n\n**Findings:**\n"
            for f in task["findings"]:
                content += f"- {f}\n"
            if task["deliverable"]:
                content += f"\n**Deliverable/Artifact:** {task['deliverable']}\n"
            if task["evidence"]:
                content += f"**Evidence:** {task['evidence']}\n"
                
            state["shared_knowledge"].append({
                "key": f"{task['project']}: {task['name']}",
                "content": content,
                "source_task_id": task_id,
                "approved_by": curr_user,
                "timestamp": datetime.now().isoformat()
            })
            print("Approved deliverables added to Shared Knowledge Base.")
    else:
        task["status"] = "NEEDS REVISION"
        print(f"QA {result}: Task '{task_id}' has been returned to {task['owner']} for revision. Status set to NEEDS REVISION.")
        
    task["updated_at"] = datetime.now().isoformat()
    log_activity(state, curr_user, task["subproject"], task["project"], task_id, "SEO TESTING & QA", f"QA Review: {result}", "SUCCESS")
    save_state(state)

def cmd_open(args):
    state = load_state()
    sess = load_local_session()
    curr_user = sess.get("current_user")
    if not curr_user:
        print("No active session. Please START first.")
        sys.exit(1)
        
    subproject = args.subproject.capitalize()
    if subproject not in state["users"]:
        print(f"Error: Named sub-project '{subproject}' does not exist.")
        sys.exit(1)
        
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    
    if role != "ADMIN" and subproject != curr_user:
        print(f"Error: You do not have permission to open '{subproject}' sub-project.")
        sys.exit(1)
        
    sess["viewing_subproject"] = subproject
    save_local_session(sess)
    
    print(f"Opening: {subproject.upper()} SUB-PROJECT")
    print(f"Role: {state['users'][subproject]['role'].replace('_', ' ').title()}")
    
    tasks = [t for tid, t in state["tasks"].items() if t["subproject"] == subproject]
    print(f"\nTasks in sub-project '{subproject}':")
    if not tasks:
        print("No tasks assigned to this sub-project.")
    else:
        for t in tasks:
            print(f"  - [{t['id']}] {t['name']} | Status: {t['status']} | Priority: {t['priority']} | QA: {t['qa_status']}")
            
    log_activity(state, curr_user, subproject, None, None, None, "Open Sub-project", "SUCCESS")
    save_state(state)

def cmd_report_member(args):
    state = load_state()
    sess = load_local_session()
    curr_user = sess.get("current_user")
    if not curr_user:
        print("No active session.")
        sys.exit(1)
        
    username = args.name.capitalize() if args.name else curr_user
    user_info = get_user_info(state, curr_user)
    role = user_info.get("role")
    
    if role != "ADMIN" and username != curr_user:
        print("Permission Denied: You can only generate your own report.")
        sys.exit(1)
        
    target_info = get_user_info(state, username)
    if not target_info:
        print(f"Error: User '{username}' not found.")
        sys.exit(1)
        
    date_str = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
    member_tasks = [t for tid, t in state["tasks"].items() if t["owner"] == username]
    
    completed = []
    in_progress = []
    blocked = []
    findings = []
    deliverables = []
    pending_qa = []
    
    for t in member_tasks:
        is_today = t["updated_at"].startswith(date_str) or t["created_at"].startswith(date_str)
        if not is_today:
            continue
            
        if t["status"] == "COMPLETED":
            completed.append(f"{t['id']}: {t['name']} (Project: {t['project']})")
        elif t["status"] == "BLOCKED":
            blocked.append(f"{t['id']}: {t['name']} (Project: {t['project']})")
        elif t["status"] == "SUBMITTED FOR QA":
            pending_qa.append(f"{t['id']}: {t['name']} (Project: {t['project']})")
        else:
            in_progress.append(f"{t['id']}: {t['name']} (Project: {t['project']})")
            
        if t["findings"]:
            findings.extend(t["findings"])
        if t["deliverable"]:
            deliverables.append(f"{t['id']} Deliverable: {t['deliverable']}")
            
    today_activities = [a for a in state["activity_log"] if a["user"] == username and a["timestamp"].startswith(date_str)]
    activity_summary = []
    for a in today_activities:
        activity_summary.append(f"- {a['action']} (Result: {a['result']}) at {a['timestamp'][11:16]}")
        
    blockers = [f"{t['id']}: {t['name']} - Blocked" for t in member_tasks if t["status"] == "BLOCKED"]
    
    print(f"# {username.upper()} DAILY SEO REPORT")
    print(f"**Date:** {date_str}")
    print(f"**Sub-project:** {username}")
    print(f"**Role:** {target_info['role'].replace('_', ' ').title()}")
    print("\n## Projects Worked On")
    projs = list(set([t["project"] for t in member_tasks if t["updated_at"].startswith(date_str)]))
    if projs:
        for p in projs:
            print(f"- {p}")
    else:
        print("None")
        
    print("\n## Tasks Completed")
    if completed:
        for c in completed:
            print(f"- {c}")
    else:
        print("None")
        
    print("\n## Tasks In Progress")
    if in_progress:
        for ip in in_progress:
            print(f"- {ip}")
    else:
        print("None")
        
    print("\n## Tasks Pending QA")
    if pending_qa:
        for pq in pending_qa:
            print(f"- {pq}")
    else:
        print("None")
        
    print("\n## Work Performed Activity")
    if activity_summary:
        for act in activity_summary:
            print(act)
    else:
        print("No logs for today.")
        
    print("\n## Important Findings")
    if findings:
        for f in findings:
            print(f"- {f}")
    else:
        print("None")
        
    print("\n## Deliverables")
    if deliverables:
        for d in deliverables:
            print(f"- {d}")
    else:
        print("None")
        
    print("\n## Blockers")
    if blockers:
        for b in blockers:
            print(f"- {b}")
    else:
        print("None")
        
    print("\n## Recommended Next Actions")
    next_actions = []
    if in_progress:
        next_actions.append("Continue working on in-progress tasks.")
    if blocked:
        next_actions.append("Resolve blockers for blocked tasks.")
    if pending_qa:
        next_actions.append("Monitor QA testing results.")
    if not next_actions:
        next_actions.append("Request new tasks from Admin.")
    for na in next_actions:
        print(f"- {na}")
        
    root = get_workspace_root()
    local_dir = os.path.join(root, "subprojects", username.lower())
    if os.path.exists(local_dir):
        report_path = os.path.join(local_dir, f"report_{date_str}.md")
        try:
            with open(report_path, 'w') as f:
                f.write(f"# {username.upper()} DAILY SEO REPORT\n")
                f.write(f"Date: {date_str}\n\n")
                f.write("## Completed Tasks\n")
                for c in completed: f.write(f"- {c}\n")
                f.write("\n## In Progress Tasks\n")
                for ip in in_progress: f.write(f"- {ip}\n")
                f.write("\n## Important Findings\n")
                for fd in findings: f.write(f"- {fd}\n")
                f.write("\n## Deliverables\n")
                for d in deliverables: f.write(f"- {d}\n")
        except Exception:
            pass

def cmd_report_team(args):
    state = load_state()
    ok, err = check_permission(state, "reports")
    if not ok:
        print(err)
        sys.exit(1)
        
    date_str = args.date if args.date else datetime.now().strftime("%Y-%m-%d")
    
    print(f"# SEO TEAM DAILY REPORT")
    print(f"**Date:** {date_str}")
    print("\n## TEAM SUMMARY")
    
    completed = []
    in_progress = []
    blocked = []
    pending_qa = []
    findings = []
    
    for tid, t in state["tasks"].items():
        is_today = t["updated_at"].startswith(date_str) or t["created_at"].startswith(date_str)
        if not is_today:
            continue
            
        desc = f"{t['id']}: {t['name']} (Owner: {t['owner']})"
        if t["status"] == "COMPLETED":
            completed.append(desc)
        elif t["status"] == "BLOCKED":
            blocked.append(desc)
        elif t["status"] == "SUBMITTED FOR QA":
            pending_qa.append(desc)
        else:
            in_progress.append(desc)
            
        if t["findings"]:
            findings.extend([f"{f} (Source: {t['id']} by {t['owner']})" for f in t["findings"]])
            
    print(f"- **Completed Tasks:** {len(completed)}")
    print(f"- **Tasks in Progress:** {len(in_progress)}")
    print(f"- **Blocked Tasks:** {len(blocked)}")
    print(f"- **Pending QA:** {len(pending_qa)}")
    
    print("\n## Completed Work Details")
    if completed:
        for c in completed: print(f"- {c}")
    else:
        print("None")
        
    print("\n## In Progress Details")
    if in_progress:
        for ip in in_progress: print(f"- {ip}")
    else:
        print("None")
        
    print("\n## Blocked Tasks Details")
    if blocked:
        for b in blocked: print(f"- {b}")
    else:
        print("None")
        
    print("\n## Pending QA Details")
    if pending_qa:
        for pq in pending_qa: print(f"- {pq}")
    else:
        print("None")
        
    print("\n## Important SEO Findings")
    if findings:
        for f in findings: print(f"- {f}")
    else:
        print("None")
        
    print("\n## Member-by-Member Summary")
    for username, info in state["users"].items():
        user_tasks = [t for tid, t in state["tasks"].items() if t["owner"] == username and (t["updated_at"].startswith(date_str) or t["created_at"].startswith(date_str))]
        print(f"\n### {username} ({info['role'].replace('_', ' ').title()})")
        if not user_tasks:
            print("No task updates today.")
        else:
            for t in user_tasks:
                print(f"- [{t['id']}] {t['name']} (Status: {t['status']})")

def cmd_knowledge(args):
    state = load_state()
    curr_user = get_current_user(state)
    if not curr_user:
        print("No active session.")
        sys.exit(1)
        
    if args.add:
        ok, err = check_permission(state, "strategy")
        if not ok:
            print(err)
            sys.exit(1)
            
        key = args.key.strip()
        content = args.content.strip()
        
        state["shared_knowledge"].append({
            "key": key,
            "content": content,
            "source_task_id": args.source_task if args.source_task else "MANUAL",
            "approved_by": curr_user,
            "timestamp": datetime.now().isoformat()
        })
        print(f"Knowledge item '{key}' added successfully.")
        log_activity(state, curr_user, curr_user, None, None, None, f"Add Shared Knowledge: {key}", "SUCCESS")
        save_state(state)
    else:
        if not state["shared_knowledge"]:
            print("No shared SEO knowledge has been approved yet.")
            return
            
        print("# SHARED APPROVED SEO KNOWLEDGE BASE\n")
        for idx, k in enumerate(state["shared_knowledge"]):
            print(f"## {idx+1}. {k['key']}")
            print(f"**Approved By:** {k['approved_by']} | **Timestamp:** {k['timestamp'][:16]}")
            if k['source_task_id']:
                print(f"**Source Task:** {k['source_task_id']}")
            print(f"\n{k['content']}")
            print("\n" + "="*40 + "\n")

def main():
    parser = argparse.ArgumentParser(description="SEO Master Operating System Engine")
    subparsers = parser.add_parser_group = parser.add_subparsers(dest="command", help="Available commands")
    
    parser_start = subparsers.add_parser("start", help="Identify yourself and start session")
    parser_start.add_argument("name", help="Your name")
    subparsers.add_parser("session", help="Check active session details")
    subparsers.add_parser("stop", help="Stop current session")
    subparsers.add_parser("users", help="List all users and permissions")
    
    parser_grant = subparsers.add_parser("grant", help="Grant permission to user")
    parser_grant.add_argument("name", help="Username")
    parser_grant.add_argument("permission", help="Permission name")
    
    parser_revoke = subparsers.add_parser("revoke", help="Revoke permission from user")
    parser_revoke.add_argument("name", help="Username")
    parser_revoke.add_argument("permission", help="Permission name")
    
    parser_cproj = subparsers.add_parser("create-project", help="Create an SEO project")
    parser_cproj.add_argument("--name", required=True, help="Project name")
    parser_cproj.add_argument("--description", required=True, help="Project description")
    subparsers.add_parser("list-projects", help="List all projects")
    
    parser_ctask = subparsers.add_parser("create-task", help="Create an SEO task")
    parser_ctask.add_argument("--name", required=True, help="Task name")
    parser_ctask.add_argument("--project", required=True, help="Project name")
    parser_ctask.add_argument("--owner", required=True, help="Task owner (Prashant, etc.)")
    parser_ctask.add_argument("--agent", required=True, help="SEO specialist agent")
    parser_ctask.add_argument("--objective", required=True, help="Task objective")
    parser_ctask.add_argument("--priority", help="Priority (HIGH/MEDIUM/LOW)")
    parser_ctask.add_argument("--collaborators", help="Comma-separated list of collaborator usernames")
    parser_ctask.add_argument("--dependencies", help="Comma-separated list of dependency Task IDs")
    
    parser_ltasks = subparsers.add_parser("list-tasks", help="List tasks")
    parser_ltasks.add_argument("--owner", help="Filter by owner")
    parser_ltasks.add_argument("--project", help="Filter by project")
    parser_ltasks.add_argument("--status", help="Filter by status")
    parser_ltasks.add_argument("--all", action="store_true", help="List all tasks regardless of active sub-project")
    
    parser_utask = subparsers.add_parser("update-task", help="Update task properties")
    parser_utask.add_argument("--id", required=True, help="Task ID")
    parser_utask.add_argument("--status", help="Task status")
    parser_utask.add_argument("--work", help="Work performed details")
    parser_utask.add_argument("--findings", help="Important findings (separated by ';;')")
    parser_utask.add_argument("--evidence", help="Evidence text/url")
    parser_utask.add_argument("--deliverable", help="Deliverable summary or artifact path")
    parser_utask.add_argument("--owner", help="Reassign task owner")
    
    parser_sub = subparsers.add_parser("submit", help="Submit task for QA testing")
    parser_sub.add_argument("--id", required=True, help="Task ID")
    
    parser_test = subparsers.add_parser("test", help="Review and QA a submitted task")
    parser_test.add_argument("--id", required=True, help="Task ID")
    parser_test.add_argument("--result", required=True, help="PASS/FAIL/NEEDS_REVISION/BLOCKED/NOT_VERIFIABLE")
    parser_test.add_argument("--feedback", help="QA Feedback notes")
    
    parser_open = subparsers.add_parser("open", help="Open a named subproject")
    parser_open.add_argument("subproject", help="Subproject name")
    
    parser_repm = subparsers.add_parser("report-member", help="Generate member report")
    parser_repm.add_argument("--name", help="Username (default: current user)")
    parser_repm.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    
    parser_rept = subparsers.add_parser("report-team", help="Generate daily team report")
    parser_rept.add_argument("--date", help="Date in YYYY-MM-DD format (default: today)")
    
    parser_know = subparsers.add_parser("knowledge", help="View or add shared knowledge")
    parser_know.add_argument("--add", action="store_true", help="Add knowledge mode")
    parser_know.add_argument("--key", help="Knowledge title")
    parser_know.add_argument("--content", help="Knowledge body content")
    parser_know.add_argument("--source-task", help="Source Task ID")
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
        
    cmds = {
        "start": cmd_start,
        "session": cmd_session,
        "stop": cmd_logout,
        "users": cmd_users,
        "grant": cmd_grant,
        "revoke": cmd_revoke,
        "create-project": cmd_create_project,
        "list-projects": cmd_list_projects,
        "create-task": cmd_create_task,
        "list-tasks": cmd_list_tasks,
        "update-task": cmd_update_task,
        "submit": cmd_submit,
        "test": cmd_test,
        "open": cmd_open,
        "report-member": cmd_report_member,
        "report-team": cmd_report_team,
        "knowledge": cmd_knowledge
    }
    
    cmds[args.command](args)

if __name__ == "__main__":
    main()
