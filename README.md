# 🐾 Sistema de Gestión Veterinaria "Veterios"

Este proyecto consiste en un ecosistema digital integral para la clínica veterinaria **Veterios**. El sistema busca digitalizar la gestión de citas, historias clínicas y la interacción con los clientes, reemplazando los procesos manuales por una solución escalable y eficiente.

## 👥 Integrantes - Grupo X

- **Almerco Ayala, Franco Raúl** (2312782)
- **Gonzales Cuaresma, Alondra Yamileth** (2312461)
- **Morales Silva, Omar Jean Piere** (2313215)
- **Kuniyoshi Zambrano, Ashley Misae** (2311528)

**Docente:** Hervert Navarro Vela

**Curso:** Desarrollo basado en plataformas

**Institución:** Universidad Tecnológica del Perú (UTP) - 2026-01

---

## 🚀 Descripción del Proyecto

"Veterios" aborda la problemática de la gestión analógica en servicios veterinarios. El ecosistema se divide en:

1. **Plataforma Web (Administración):** Desarrollada para que el administrador y los veterinarios gestionen la clínica.
2. **Aplicación Móvil (Cliente):** Orientada al dueño de la mascota para agendar citas y revisar historiales médicos.

## 🛠️ Stack Tecnológico

- **Backend:** [Django](https://www.djangoproject.com/) (Python)
- **Frontend Web:** HTML5, CSS3, JavaScript
- **Base de Datos:** PostgreSQL
- **Aplicación Móvil:** Android Studio (Java/Kotlin)
- **Generación de Documentos:** ReportLab / WeasyPrint (PDFs de historias clínicas)

---

## ✨ Funcionalidades Principales

### 🔑 Módulo de Usuarios y Seguridad

- Roles diferenciados: **Administrador, Veterinario y Cliente**.
- Autenticación segura y gestión de perfiles.

### 🐕 Gestión de Mascotas y Citas

- Registro detallado de pacientes (especie, raza, sexo, edad).
- Sistema de agendamiento autónomo para clientes.
- Dashboard administrativo para asignación de médicos y control de horarios.

### 🩺 Módulo Médico

- Creación de historias clínicas digitales.
- Registro de diagnósticos, tratamientos y recetas.
- Exportación de expedientes médicos en formato PDF.

---

## 📐 Arquitectura

El sistema sigue una arquitectura de **N-Capas** para asegurar la separación de responsabilidades:

- **Capa de Presentación:** Interfaz Web (Django Templates) y App Móvil (Android).
- **Capa de Lógica de Negocio:** Servicios y modelos en Django.
- **Capa de Datos:** Persistencia en PostgreSQL.

---

## 🛠️ Instalación y Configuración (Backend Web)

1. **Clonar el repositorio:**Bash
    
    `git clone https://github.com/tu-usuario/veterios-proyecto.git
    cd veterios-proyecto`
    
2. **Crear y activar un entorno virtual:**Bash
    
    `python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Mac/Linux:
    source venv/bin/activate`
    
3. **Instalar dependencias:**Bash
    
    `pip install -r requirements.txt`
    
4. **Configurar la base de datos:** Asegúrate de tener PostgreSQL corriendo y configurar las credenciales en el archivo `settings.py`. Luego ejecuta:Bash
    
    `python manage.py makemigrations
    python manage.py migrate`
    
5. **Iniciar el servidor:**Bash
    
    `python manage.py runserver`
    

---

## 📱 Configuración (App Móvil)

1. Abrir la carpeta `mobile_app/` en **Android Studio**.
2. Sincronizar el proyecto con archivos **Gradle**.
3. Cambiar la URL base de la API en el archivo de configuración para que apunte a la dirección IP de tu servidor Django.
4. Compilar y ejecutar en un emulador o dispositivo físico.

---

## 📊 Resultados Esperados

- Centralización del 100% de las historias clínicas.
- Reducción del tiempo de respuesta en la búsqueda de antecedentes médicos a menos de 3 segundos.
- Eliminación de errores por cruce de horarios en citas médicas.

## 📄 Licencia

Este proyecto fue realizado con fines académicos para la carrera de Ingeniería de Software.

---

*Lima, Perú - 2026*
