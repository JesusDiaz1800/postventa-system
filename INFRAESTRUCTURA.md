# Contexto de Infraestructura - Sistema Postventa

## Arquitectura
```
[Servidor RDP 192.168.1.234]  <--Red Interna-->  [PCs Empleados]
     |                                                 |
   Vite + Django                              Navegador Chrome/Edge
   (Sin admin)                                (Certificado instalado por TI)
```

## Configuración del Servidor (Escritorio Remoto)
- **Ubicación**: Escritorio Remoto Windows (RDP) sobre red de Polifusion
- **IP Fija**: 192.168.1.234
- **Puerto Frontend**: 5173 (Vite HTTPS)
- **Puerto Backend**: 8000 (Django ASGI/Daphne)
- **Permisos**: El usuario jdiaz NO tiene privilegios de administrador en este servidor.

## Acceso de Usuarios (Empleados)
- Los colaboradores acceden mediante: `https://192.168.1.234:5173`
- TI instala el certificado raíz (carpeta `PARA_TI`) en cada PC de empleado.
- Después de instalación, los empleados NO ven advertencias de seguridad.

## Nota Importante para el Desarrollador (jdiaz)
**Los errores de certificado que ves en tu navegador del servidor RDP son NORMALES.**
- Tú no tienes admin para instalar el certificado en el servidor.
- Los errores solo afectan TU navegador, no el de los usuarios.
- Los usuarios con certificado instalado verán la app correctamente.
- Para probar la app tú mismo, usa "Continuar de todos modos" o pide a TI que instale el cert en el servidor.

## Archivos de Distribución
- `PARA_TI/` - Kit para que TI instale certificados en PCs de empleados.
- `ACCESO_CLIENTES/` - Alternativa si empleados tienen admin en sus PCs.
