# Guía: Instalación de Certificado y App Desktop (PWA)

Para que el sistema funcione correctamente, sea instalable y no muestre advertencias de "Conexión no privada", debes instalar el **Certificado de Confianza de Polifusión**.

## 1. Descargar el Certificado
En la página de inicio de sesión, haz clic en el botón **"Configuración de Seguridad"** y luego en **"Descargar Certificado Root CA"**. 
Alternativamente, puedes descargarlo directamente desde este enlace (si estás en la red): `https://[IP-SERVIDOR]/api/users/download-ca/`

## 2. Instalar en Windows (Chrome/Edge/Chrome)
Sigue estos pasos para eliminar la advertencia de seguridad:

1.  Busca el archivo descargado (`Polifusion-CA.crt`) y haz doble clic en él.
2.  Haz clic en **"Instalar certificado..."**.
3.  Selecciona **"Usuario actual"** y dale a Siguiente.
4.  Selecciona la opción **"Colocar todos los certificados en el siguiente almacén"**.
5.  Haz clic en **"Examinar..."**.
6.  **IMPORTANTE**: Selecciona **"Entidades de certificación raíz de confianza"**.
7.  Acepta, dale a Siguiente y luego a **Finalizar**.
8.  Aparecerá una advertencia de seguridad de Windows, haz clic en **SÍ**.
9.  **Reinicia tu navegador**.

## 3. Instalar la Aplicación en el Escritorio
Una vez que el certificado esté instalado y el navegador muestre el candado gris (sin advertencias rojas):

1.  En la barra de direcciones (derecha), aparecerá un icono de una pantalla con una flecha: **"Instalar Sistema de Postventa"**.
2.  Haz clic en él y selecciona **Instalar**.
3.  Ahora tendrás un acceso directo en tu escritorio y menú de inicio que abre el sistema como una aplicación independiente.

---
> [!TIP]
> Si usas un dispositivo móvil (Android/iOS), el proceso es similar: descarga el certificado, ve a ajustes de seguridad/certificados e instálalo como "Certificado CA" o "Root".
