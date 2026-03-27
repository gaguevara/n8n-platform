import json
import os

GIT_WORKFLOW = "app/workflows/threat-intel-main.json"
STAGING_EXPORT = ".tmp/codex-staging/threat-intel-main.reimport-verify-2026-03-25.json"

def compare_workflows():
    if not os.path.exists(GIT_WORKFLOW) or not os.path.exists(STAGING_EXPORT):
        print(f"[!] Error: Archivos no encontrados para comparación.")
        return

    with open(GIT_WORKFLOW, 'r', encoding='utf-8-sig') as f:
        git_wf = json.load(f)
    
    with open(STAGING_EXPORT, 'r', encoding='utf-8-sig') as f:
        staging_wf = json.load(f)
        if isinstance(staging_wf, list):
            staging_wf = staging_wf[0]

    git_nodes = {n['id']: n for n in git_wf.get('nodes', [])}
    staging_nodes = {n['id']: n for n in staging_wf.get('nodes', [])}

    print(f"=== Análisis de Diff: Git vs Staging Export ===")
    
    # 1. Comparar Nodos
    all_ids = set(git_nodes.keys()) | set(staging_nodes.keys())
    for nid in all_ids:
        if nid not in git_nodes:
            print(f"[+] Nodo en Staging pero NO en Git: {nid} ({staging_nodes[nid].get('name')})")
            continue
        if nid not in staging_nodes:
            print(f"[-] Nodo en Git pero NO en Staging: {nid} ({git_nodes[nid].get('name')})")
            continue
        
        g_node = git_nodes[nid]
        s_node = staging_nodes[nid]
        
        # Comparar jsCode
        g_code = g_node.get('parameters', {}).get('jsCode', '')
        s_code = s_node.get('parameters', {}).get('jsCode', '')
        
        if g_code != s_code:
            print(f"[!] DRIFT en jsCode: Nodo '{g_node.get('name')}' ({nid})")
            print(f"    Git chars: {len(g_code)} vs Staging chars: {len(s_code)}")
            if "=== COPIAR CONTENIDO" in s_code or "// Placeholder" in s_code:
                print(f"    ⚠️ Staging conserva PLACEHOLDER.")
        
        # Comparar typeVersion
        if g_node.get('typeVersion') != s_node.get('typeVersion'):
            print(f"[*] Cambio Cosmético (typeVersion): {g_node.get('name')} -> Git:{g_node.get('typeVersion')} vs Staging:{s_node.get('typeVersion')}")

    # 2. Comparar Settings
    g_settings = git_wf.get('settings', {})
    s_settings = staging_wf.get('settings', {})
    if g_settings.get('errorWorkflow') != s_settings.get('errorWorkflow'):
        print(f"[!] DRIFT en Settings (errorWorkflow): Git:{g_settings.get('errorWorkflow')} vs Staging:{s_settings.get('errorWorkflow')}")

if __name__ == "__main__":
    compare_workflows()
