function openPopup() {
    document.getElementById('popup').style.display = 'flex';
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
}



async function login() {
    const nombreUsuario = document.getElementById('usuario').value.trim();
    const contraseña = document.getElementById('contrasena').value.trim();

    console.log('Datos a enviar:', { 
        nombre_usuario: nombreUsuario,
        // No imprimas la contraseña en producción
    });

    const datos = {
        nombre_usuario: nombreUsuario,
        contraseña: contraseña
    };
    
    try {
        const response = await fetch('http://127.0.0.1:5000/login_autenticacion', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(datos)
        });

        console.log('Status:', response.status);
        const data = await response.json();
        console.log('Respuesta del servidor:', data);

        // ... resto del código

        if (response.ok) {
            // Guardar datos de sesión
            localStorage.setItem('authToken', data.token);
            localStorage.setItem('userId', data.id_usuario);
            localStorage.setItem('userRole', data.cargo);
            localStorage.setItem('userName', data.nombre_completo);
            localStorage.setItem('userType', data.tipo_usuario);
            localStorage.setItem('userRut', data.rut);
            
            // Redirigir según el tipo de usuario
            switch(data.tipo_usuario.toLowerCase()) {
                case 'administrador':
                    window.location.href = '/home';
                    break;
                case 'tiempocompleto':
                    window.location.href = '/home';
                    break;
                default:
                    window.location.href = '/home';
            }
        } else {
            const mensaje = data.error || 'Error desconocido';
            alert(`Error: ${mensaje}`);
            document.getElementById('contrasena').value = '';
        }
    } catch (err) {
        console.error('Error:', err);
        alert('Error de conexión con el servidor. Por favor, intenta más tarde.');
    }
}
// Agregar evento para manejar el formulario de recuperación de contraseña
document.addEventListener('DOMContentLoaded', function() {
    const recoveryForm = document.querySelector('#popup form');
    if (recoveryForm) {
        recoveryForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value.trim();

            try {
                const response = await fetch('http://127.0.0.1:5000/recuperar_password', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email })
                });

                const data = await response.json();
                
                if (response.ok) {
                    alert('Se han enviado las instrucciones a tu correo');
                    closePopup();
                } else {
                    alert('Error: ' + (data.error || 'No se pudo procesar la solicitud'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error de conexión con el servidor');
            }
        });
    }
});