# Proto Watch Installation (SPEC-005)

## Linux / systemd

1. Copiar `framework-watch.service` a `/etc/systemd/system/framework-watch.service`
2. Ajustar `WorkingDirectory` y `ExecStart`
3. Ejecutar:
   - `sudo systemctl daemon-reload`
   - `sudo systemctl enable --now framework-watch.service`

## Windows / Task Scheduler

1. Revisar rutas en `install_watch_task.ps1`
2. Ejecutar PowerShell como administrador
3. Correr:
   - `powershell -ExecutionPolicy Bypass -File .multiagent\templates\proto_watch\install_watch_task.ps1`

## Git Hook

1. Copiar `post-commit.sample` a `.git/hooks/post-commit`
2. Dar permisos de ejecución si aplica
3. El hook ejecuta `proto_watch.py --once` al cerrar un commit
