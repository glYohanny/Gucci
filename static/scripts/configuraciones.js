// Función para mostrar alertas
function showAlert(message, type = 'info') {
    alert(message);
}

// Función para guardar configuraciones
function guardarConfiguracion(configId) {
    const elemento = document.getElementById(configId);
    let valor;
    
    if (elemento.type === 'checkbox') {
        valor = elemento.checked;
    } else {
        valor = elemento.value;
    }

    // Aquí se simula el guardado de la configuración
    showAlert(`Configuración "${configId}" guardada correctamente: ${valor}`);
}

// Función para realizar respaldo
function realizarRespaldo() {
    showAlert('Iniciando proceso de respaldo...', 'info');
    
    // Simular proceso de respaldo
    setTimeout(() => {
        showAlert('Respaldo completado exitosamente', 'success');
    }, 2000);
}

// Event Listener cuando se carga el documento
document.addEventListener('DOMContentLoaded', function() {
    console.log('Página de configuraciones cargada');
    showAlert('Bienvenido a la página de configuraciones');
});

// Función para manejar errores
function handleError(error) {
    showAlert(`Error: ${error.message}`, 'error');
    console.error('Error:', error);
}