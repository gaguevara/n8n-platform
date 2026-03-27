import json
import os
import sys

# Mapeo de IDs de nodos en n8n a archivos .js en app/code-nodes/
NODE_MAPPING = {
    "code-normalizer": "ioc_normalizer.js",
    "code-persist": "ioc_persistence.js",
    "code-alert": "alert_dispatcher.js"
}

WORKFLOW_PATH = "app/workflows/threat-intel-main.json"
CODE_NODES_DIR = "app/code-nodes"

def inject_code():
    print(f"[*] Iniciando inyección de código en {WORKFLOW_PATH}...")
    
    if not os.path.exists(WORKFLOW_PATH):
        print(f"[!] Error: No se encuentra el archivo de workflow en {WORKFLOW_PATH}")
        sys.exit(1)

    with open(WORKFLOW_PATH, 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    modified = False
    for node in workflow.get("nodes", []):
        node_id = node.get("id")
        if node_id in NODE_MAPPING:
            js_file = NODE_MAPPING[node_id]
            js_path = os.path.join(CODE_NODES_DIR, js_file)
            
            if os.path.exists(js_path):
                print(f"[*] Inyectando {js_file} en nodo '{node.get('name')}' ({node_id})...")
                with open(js_path, 'r', encoding='utf-8') as js_f:
                    js_code = js_f.read()
                
                # Actualizar el parámetro jsCode
                if "parameters" not in node:
                    node["parameters"] = {}
                
                old_code = node["parameters"].get("jsCode", "")
                if old_code != js_code:
                    node["parameters"]["jsCode"] = js_code
                    modified = True
                    print(f"[+] Nodo '{node_id}' actualizado ({len(js_code)} chars).")
                else:
                    print(f"[-] Nodo '{node_id}' ya está al día.")
            else:
                print(f"[!] Advertencia: No se encuentra el archivo {js_path}")

    if modified:
        with open(WORKFLOW_PATH, 'w', encoding='utf-8') as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"[✅] Workflow actualizado exitosamente.")
    else:
        print(f"[*] No se requirieron cambios en el workflow.")

if __name__ == "__main__":
    inject_code()
