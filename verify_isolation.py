import os
import subprocess
import sys
import json

def run_cmd(cwd, args):
    cmd = ["python", os.path.join("C:\\Users\\Dived Mishra\\.gemini\\antigravity\\scratch\\seo_team", "seo_master.py")] + args
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout, res.stderr

def print_result(step, code, out, err, expect_fail=False):
    print(f"=== STEP: {step} ===")
    print(f"Exit Code: {code} (Expected {'Fail' if expect_fail else 'Success'})")
    if out:
        print(f"Stdout:\n{out.strip()}")
    if err:
        print(f"Stderr:\n{err.strip()}")
    print("-" * 50)
    
    if expect_fail and code == 0:
        print(f"Error: Step {step} succeeded but was expected to fail!")
        sys.exit(1)
    if not expect_fail and code != 0:
        print(f"Error: Step {step} failed but was expected to succeed!")
        sys.exit(1)

def main():
    root = "C:\\Users\\Dived Mishra\\.gemini\\antigravity\\scratch\\seo_team"
    os.chdir(root)
    
    prashant_dir = os.path.join(root, "subprojects", "prashant")
    kanishak_dir = os.path.join(root, "subprojects", "kanishak")
    workspace_root = root
    
    # 1. Clean up old session files if they exist
    for d in [prashant_dir, kanishak_dir, workspace_root]:
        sess_file = os.path.join(d, ".session.json")
        if os.path.exists(sess_file):
            os.remove(sess_file)
            
    # Reset database state
    db_file = os.path.join(root, "seo_state.json")
    clean_data = {
      "users": {
        "Dived": {"role": "ADMIN", "permissions": ["on_page", "off_page", "technical", "research", "intelligence", "testing", "strategy", "projects", "team_management", "reports"]},
        "Chirag": {"role": "ADMIN", "permissions": ["on_page", "off_page", "technical", "research", "intelligence", "testing", "strategy", "projects", "team_management", "reports"]},
        "Ravi": {"role": "ADMIN", "permissions": ["on_page", "off_page", "technical", "research", "intelligence", "testing", "strategy", "projects", "team_management", "reports"]},
        "Prashant": {"role": "TEAM MEMBER", "permissions": ["off_page"]},
        "Kanishak": {"role": "TEAM MEMBER", "permissions": ["off_page"]}
      },
      "projects": {},
      "tasks": {},
      "activity_log": [],
      "shared_knowledge": [],
      "strategy": "Initial shared SEO strategy."
    }
    with open(db_file, 'w') as f:
        json.dump(clean_data, f, indent=2)
        
    print("Database reset to clean state.")
    print("-" * 50)
    
    # 2. Admin logs in from workspace root to setup project and tasks
    code, out, err = run_cmd(workspace_root, ["start", "Dived"])
    print_result("Admin Dived START", code, out, err)
    
    code, out, err = run_cmd(workspace_root, ["create-project", "--name", "Competitor Backlink Research", "--description", "Competitor link profile audit"])
    print_result("Admin Create Project", code, out, err)
    
    # Create Tasks
    code, out, err = run_cmd(workspace_root, ["create-task", "--name", "Analyze Klaviyo backlinks", "--project", "Competitor Backlink Research", "--owner", "Prashant", "--agent", "OFF-PAGE & AUTHORITY", "--objective", "Find backlinks for Klaviyo"])
    print_result("Create Task 1 (Prashant)", code, out, err)
    
    code, out, err = run_cmd(workspace_root, ["create-task", "--name", "Analyze Mailchimp backlinks", "--project", "Competitor Backlink Research", "--owner", "Kanishak", "--agent", "OFF-PAGE & AUTHORITY", "--objective", "Find backlinks for Mailchimp"])
    print_result("Create Task 2 (Kanishak)", code, out, err)
    
    # Log out Admin
    code, out, err = run_cmd(workspace_root, ["stop"])
    print_result("Admin Dived STOP", code, out, err)
    
    # Verify Admin session is removed at root
    root_sess = os.path.join(workspace_root, ".session.json")
    if os.path.exists(root_sess):
        print("Error: Root session file still exists after stop!")
        sys.exit(1)
        
    # 3. Simulate simultaneous logins in subproject directories
    # Log in Prashant in subprojects/prashant/
    code, out, err = run_cmd(prashant_dir, ["start", "Prashant"])
    print_result("Prashant Session START (in subprojects/prashant)", code, out, err)
    
    # Log in Kanishak in subprojects/kanishak/
    code, out, err = run_cmd(kanishak_dir, ["start", "Kanishak"])
    print_result("Kanishak Session START (in subprojects/kanishak)", code, out, err)
    
    # Verify BOTH session files exist concurrently
    prashant_sess = os.path.join(prashant_dir, ".session.json")
    kanishak_sess = os.path.join(kanishak_dir, ".session.json")
    
    if not os.path.exists(prashant_sess) or not os.path.exists(kanishak_sess):
        print("Error: Concurrently active session files were not found!")
        sys.exit(1)
        
    # Read session details to confirm
    with open(prashant_sess) as f:
        p_data = json.load(f)
        if p_data.get("current_user") != "Prashant":
            print(f"Error: Prashant's session file has wrong user: {p_data}")
            sys.exit(1)
            
    with open(kanishak_sess) as f:
        k_data = json.load(f)
        if k_data.get("current_user") != "Kanishak":
            print(f"Error: Kanishak's session file has wrong user: {k_data}")
            sys.exit(1)
            
    print("CONCURRENT SESSIONS CONFIRMED: Prashant and Kanishak logged in independently.")
    print("-" * 50)
    
    # 4. Verify Prashant sees only TSK-001, Kanishak sees only TSK-002
    code, out, err = run_cmd(prashant_dir, ["list-tasks"])
    print_result("Prashant List Tasks", code, out, err)
    if "TSK-001" not in out or "TSK-002" in out:
        print("Error: Prashant's task list is not isolated! Output was:")
        print(out)
        sys.exit(1)
        
    code, out, err = run_cmd(kanishak_dir, ["list-tasks"])
    print_result("Kanishak List Tasks", code, out, err)
    if "TSK-002" not in out or "TSK-001" in out:
        print("Error: Kanishak's task list is not isolated! Output was:")
        print(out)
        sys.exit(1)
        
    print("ISOLATED TASK VISIBILITY CONFIRMED.")
    print("-" * 50)
    
    # 5. Prashant updates TSK-001, Kanishak updates TSK-002 (simultaneous work simulation)
    code, out, err = run_cmd(prashant_dir, [
        "update-task", "--id", "TSK-001", "--status", "IN PROGRESS", 
        "--work", "Prashant backlink audit completed.", "--findings", "Klaviyo has 200 referring domains"
    ])
    print_result("Prashant Updates TSK-001", code, out, err)
    
    code, out, err = run_cmd(kanishak_dir, [
        "update-task", "--id", "TSK-002", "--status", "IN PROGRESS", 
        "--work", "Kanishak backlink audit completed.", "--findings", "Mailchimp has 400 referring domains"
    ])
    print_result("Kanishak Updates TSK-002", code, out, err)
    
    # 6. Verify cross-updates are blocked (Prashant trying to update Kanishak's task TSK-002)
    code, out, err = run_cmd(prashant_dir, ["update-task", "--id", "TSK-002", "--status", "COMPLETED"])
    print_result("Prashant tries to update Kanishak task (should fail)", code, out, err, expect_fail=True)
    
    # 7. Log out Prashant, Kanishak session should still be alive
    code, out, err = run_cmd(prashant_dir, ["stop"])
    print_result("Prashant STOP", code, out, err)
    
    if os.path.exists(prashant_sess):
        print("Error: Prashant's session file was not removed on stop!")
        sys.exit(1)
        
    if not os.path.exists(kanishak_sess):
        print("Error: Kanishak's session file was accidentally removed on Prashant stop!")
        sys.exit(1)
        
    print("ISOLATED LOGOUT CONFIRMED: Prashant logged out, Kanishak is still logged in.")
    print("-" * 50)
    
    # Kanishak log out
    code, out, err = run_cmd(kanishak_dir, ["stop"])
    print_result("Kanishak STOP", code, out, err)
    
    if os.path.exists(kanishak_sess):
        print("Error: Kanishak's session file was not removed on stop!")
        sys.exit(1)
        
    print("ALL ISOLATION VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
