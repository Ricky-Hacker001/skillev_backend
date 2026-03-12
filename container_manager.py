import docker
import socket
import time
import threading
from datetime import datetime
from sqlalchemy.sql import func

# Internal Imports
from database import SessionLocal
import models 

client = docker.from_env()

def find_free_port():
    """Finds an available port on the host machine dynamically."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def get_or_create_room_network(domain: str):
    """Creates a standard bridge network for the domain."""
    network_name = f"{domain}_room_net"
    try:
        return client.networks.get(network_name)
    except docker.errors.NotFound:
        return client.networks.create(network_name, driver="bridge")

def cleanup_existing_task(user_id, task_id, mode):
    """
    TOTAL ISOLATION: Nukes any existing container for this specific user, 
    task, AND mode to ensure a 100% fresh start.
    """
    container_name = f"skillev_{user_id}_{task_id}_{mode}"
    try:
        container = client.containers.get(container_name)
        container.remove(force=True)
        print(f"🧹 CLEANUP: Nuked isolated container {container_name}")
    except docker.errors.NotFound:
        pass
    except Exception as e:
        print(f"⚠️ Cleanup Warning: {e}")

def capture_evidence_engine(container_id, user_id, domain, task_id, mode):
    """
    Streams logs from Docker and commits them to a fresh DB entry.
    Updated with Error Handling to prevent race-condition crashes.
    """
    db = SessionLocal()
    try:
        # 1. Verification: Ensure container still exists before attaching
        try:
            container = client.containers.get(container_id)
        except docker.errors.NotFound:
            print(f"ℹ️ Engine: Container {container_id} not found (likely nuked by cleanup).")
            return

        # 2. Create a brand new EvidenceReport entry
        report = models.EvidenceReport(
            user_id=user_id,
            domain=domain,
            task_id=task_id,
            container_id=container_id,
            mode=mode, 
            logs=[],
            status="active"
        )
        db.add(report)
        db.commit()
        db.refresh(report)

        # 3. Stream logs and tag them
        # Wrap in another try-except to catch container removal during streaming
        try:
            for line in container.logs(stream=True, follow=True, tail=0):
                log_entry = line.decode('utf-8').strip()
                
                # Tag for aggregate history clarity
                tagged_message = f"[MODE:{mode.upper()}] {log_entry}"
                
                new_event = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "stdout",
                    "message": tagged_message
                }

                db.refresh(report)
                current_logs = list(report.logs) if report.logs else []
                current_logs.append(new_event)
                report.logs = current_logs

                # Success Detection
                if "SUCCESS" in log_entry.upper():
                    report.status = "completed"
                    report.completed_at = datetime.now()
                    print(f"✅ SEALED: {mode.upper()} evidence for User {user_id}")
                
                db.commit()
        except docker.errors.APIError:
            print(f"ℹ️ Engine: Log stream for {container_id} stopped (container closed).")
                
    except Exception as e:
        print(f"⚠️ Evidence Engine Error: {e}")
    finally:
        db.close()

def start_sub_room_container(user_id: int, domain: str, task_id: str, mode: str = "hiring"):
    """
    Orchestrates the lifecycle of an isolated lab environment.
    """
    get_or_create_room_network(domain)
    
    container_name = f"skillev_{user_id}_{task_id}_{mode}"
    
    image_map = {
        "sql-injection": "skillev-labs-sqli:v5",
        "broken-auth": "skillev-labs-auth:V2",
        "idor": "skillev-labs-idor:v1",
        "input-validation": "skillev-labs-validation:v1",
        "secure-fix": "skillev-labs-fix:v1",
        "api-design": "skillev-labs-rest:v1",
        "fullstack-link": "skillev-labs-fullstack-link:v1",
        "task-management-api": "skillev-labs-crud:v1",
        "task-manager": "skillev-labs-task-manager:v1"
    }
    
    image = image_map.get(task_id)
    if not image:
        return None, f"Image not found for task: {task_id}"

    # 1. Clear previous session for THIS mode
    cleanup_existing_task(user_id, task_id, mode)

    # 2. Assign dynamic port
    assigned_port = find_free_port()

    # 3. Launch isolated container
    try:
        container = client.containers.run(
            image=image,
            name=container_name,
            network=f"{domain}_room_net",
            detach=True,
            environment={"LAB_MODE": mode},
            mem_limit="256m",
            nano_cpus=500000000, 
            ports={'5000/tcp': ('127.0.0.1', assigned_port)}, 
            labels={
                "user_id": str(user_id),
                "task_id": task_id,
                "mode": mode,
            }
        )

        # 4. Wait for the service to be healthy
        is_ready = False
        for _ in range(50): 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5) 
                if s.connect_ex(('127.0.0.1', assigned_port)) == 0:
                    time.sleep(1.0) 
                    is_ready = True
                    break
            time.sleep(0.2) 

        if is_ready:
            # 5. Start background logging thread
            threading.Thread(
                target=capture_evidence_engine, 
                args=(container.id, user_id, domain, task_id, mode), 
                daemon=True
            ).start()
            
            return {"container_id": container.id, "port": assigned_port}, None
        
        return {"container_id": container.id, "port": assigned_port}, "Service initialization timeout."

    except Exception as e:
        return None, f"Docker Orchestration Error: {str(e)}"

def kill_sub_room(container_id: str):
    """Terminates an isolated lab node."""
    try:
        container = client.containers.get(container_id)
        container.stop(timeout=2)
        container.remove()
        return True
    except Exception:
        return False