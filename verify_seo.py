import os
import subprocess
import sys

def run_cmd(args):
    cmd = ["python", "seo_master.py"] + args
    res = subprocess.run(cmd, capture_output=True, text=True)
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
    # Ensure starting in the right directory
    os.chdir("C:\\Users\\Dived Mishra\\.gemini\\antigravity\\scratch\\seo_team")
    
    # 1. Start Prashant
    code, out, err = run_cmd(["start", "Prashant"])
    print_result("Start Prashant Session", code, out, err)
    
    # 2. Try to create project (should fail - Prashant has no projects permission)
    code, out, err = run_cmd(["create-project", "--name", "Competitor Backlink Research", "--description", "Competitor Link Building Research"])
    print_result("Create Project as Prashant", code, out, err, expect_fail=True)
    
    # 3. Stop Prashant session
    code, out, err = run_cmd(["stop"])
    print_result("Stop Prashant Session", code, out, err)
    
    # 4. Start Dived (Admin)
    code, out, err = run_cmd(["start", "Dived"])
    print_result("Start Dived Session", code, out, err)
    
    # 5. Create project as Dived (should succeed)
    code, out, err = run_cmd(["create-project", "--name", "Competitor Backlink Research", "--description", "Competitor Link Building Research"])
    print_result("Create Project as Dived", code, out, err)
    
    # 6. Create Task 1 for Prashant
    code, out, err = run_cmd([
        "create-task",
        "--name", "Analyze Klaviyo backlinks",
        "--project", "Competitor Backlink Research",
        "--owner", "Prashant",
        "--agent", "OFF-PAGE & AUTHORITY",
        "--objective", "Find referring domains for Klaviyo"
    ])
    print_result("Create Task 1 for Prashant", code, out, err)
    
    # 7. Create Task 2 for Kanishak
    code, out, err = run_cmd([
        "create-task",
        "--name", "Analyze Mailchimp backlinks",
        "--project", "Competitor Backlink Research",
        "--owner", "Kanishak",
        "--agent", "OFF-PAGE & AUTHORITY",
        "--objective", "Find referring domains for Mailchimp"
    ])
    print_result("Create Task 2 for Kanishak", code, out, err)
    
    # 8. Log out Dived
    code, out, err = run_cmd(["stop"])
    print_result("Stop Dived Session", code, out, err)
    
    # 9. Log in Prashant
    code, out, err = run_cmd(["start", "Prashant"])
    print_result("Start Prashant Session again", code, out, err)
    
    # 10. Update Task 1 status and findings
    code, out, err = run_cmd([
        "update-task",
        "--id", "TSK-001",
        "--status", "IN PROGRESS",
        "--work", "Found 15 high-authority referring domains for Klaviyo.",
        "--findings", "Competitor Klaviyo has high authority domains;;Domains are relevant to email marketing",
        "--deliverable", "klaviyo_backlinks_sheet.csv"
    ])
    print_result("Update Task 1", code, out, err)
    
    # 11. Submit Task 1 for QA
    code, out, err = run_cmd(["submit", "--id", "TSK-001"])
    print_result("Submit Task 1 for QA", code, out, err)
    
    # 12. Stop Prashant
    code, out, err = run_cmd(["stop"])
    print_result("Stop Prashant Session", code, out, err)
    
    # 13. Log in Ravi (Admin)
    code, out, err = run_cmd(["start", "Ravi"])
    print_result("Start Ravi Session", code, out, err)
    
    # 14. Review and approve Task 1
    code, out, err = run_cmd([
        "test",
        "--id", "TSK-001",
        "--result", "PASS",
        "--feedback", "Excellent links, verified and approved."
    ])
    print_result("QA Pass Task 1", code, out, err)
    
    # 15. Generate individual report for Prashant
    code, out, err = run_cmd(["report-member", "--name", "Prashant"])
    print_result("Prashant Individual Report", code, out, err)
    
    # 16. Generate team report
    code, out, err = run_cmd(["report-team"])
    print_result("Team Report", code, out, err)
    
    # 17. Grant Prashant technical permission
    code, out, err = run_cmd(["grant", "Prashant", "technical"])
    print_result("Grant Technical SEO permission to Prashant", code, out, err)
    
    # 18. Stop Ravi session
    code, out, err = run_cmd(["stop"])
    print_result("Stop Ravi Session", code, out, err)
    
    # 19. Start Prashant again to verify new permission
    code, out, err = run_cmd(["start", "Prashant"])
    print_result("Start Prashant Session to Verify Permissions", code, out, err)
    
    # 20. Stop Prashant session
    code, out, err = run_cmd(["stop"])
    print_result("Clean up stop Prashant session", code, out, err)
    
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
