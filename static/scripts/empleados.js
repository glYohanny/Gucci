// Variables globales
let data = [];
const rowsPerPage = 10;
let currentPage = 1;
let editMode = false;
let currentEmployeeId = null;
let comunasPorRegion = new Map();

// Validación y formateo de RUT
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el campo RUT
    const rutInput = document.querySelector('input[name="rut"]');
    if (!rutInput) return;

    // Modificar los atributos del campo RUT
    rutInput.setAttribute('maxlength', '12');
    rutInput.setAttribute('id', 'rut');
    rutInput.setAttribute('autocomplete', 'off');
    
    // Función para formatear RUT
    function formatearRut(rut) {
        // Eliminar puntos y guión
        rut = rut.replace(/\./g, '').replace(/-/g, '');
        
        // Obtener el cuerpo y dígito verificador
        let cuerpo = rut.slice(0, -1);
        let dv = rut.slice(-1).toUpperCase();
        
        // Formatear cuerpo con puntos
        cuerpo = cuerpo.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        
        // Retornar RUT formateado
        return cuerpo + '-' + dv;
    }

    // Función para validar RUT
    function validarRut(rut) {
        // Limpiar RUT
        rut = rut.replace(/\./g, '').replace(/-/g, '');
        
        // Verificar largo mínimo
        if (rut.length < 2) return false;
        
        // Separar cuerpo y dígito verificador
        let cuerpo = rut.slice(0, -1);
        let dv = rut.slice(-1).toUpperCase();
        
        // Calcular dígito verificador
        let suma = 0;
        let multiplicador = 2;
        
        // Calcular suma ponderada
        for (let i = cuerpo.length - 1; i >= 0; i--) {
            suma += parseInt(cuerpo[i]) * multiplicador;
            multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
        }
        
        // Calcular dígito verificador esperado
        let dvEsperado = 11 - (suma % 11);
        dvEsperado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString();
        
        // Comparar dígito verificador
        return dv === dvEsperado;
    }

    // Event listener para formateo mientras se escribe
    rutInput.addEventListener('input', function(e) {
        let rut = e.target.value;
        
        // Permitir solo números, k y K
        rut = rut.replace(/[^0-9kK]/g, '');
        
        // Formatear RUT
        if (rut.length > 1) {
            rut = formatearRut(rut);
        }
        
        // Actualizar valor
        e.target.value = rut;
        
        // Validar RUT
        if (rut.length > 0) {
            if (validarRut(rut)) {
                rutInput.setCustomValidity('');
            } else {
                rutInput.setCustomValidity('RUT inválido');
            }
        } else {
            rutInput.setCustomValidity('');
        }
    });

    // Validar al perder el foco
    rutInput.addEventListener('blur', function(e) {
        let rut = e.target.value;
        if (rut && !validarRut(rut)) {
            alert('El RUT ingresado no es válido');
            e.target.focus();
        }
    });
});

// Función para obtener los datos
async function fetchData() {
    console.log('Iniciando fetchData...');
    try {
        const response = await fetch('http://localhost:5000/empleados/tabla_empleados');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        data = await response.json();
        console.log('Datos recibidos:', data);
        renderTable(currentPage);
        renderPagination();
    } catch (error) {
        console.error('Error en fetchData:', error);
        alert('Error al cargar los datos de empleados');
    }
}

// Cargar regiones
async function loadRegiones() {
    try {
        const response = await fetch('http://localhost:5000/empleados/regiones');
        if (!response.ok) throw new Error('Error al cargar regiones');
        const regiones = await response.json();
        
        const select = document.getElementById('region-select');
        select.innerHTML = '<option value="">Seleccione una región</option>';
        
        regiones.forEach(region => {
            const option = document.createElement('option');
            option.value = region.id;
            option.textContent = region.nombre;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando regiones:', error);
        alert('Error al cargar las regiones');
    }
}

// Cargar comunas según la región seleccionada
async function loadComunas(regionId) {
    try {
        console.log('Cargando comunas para región:', regionId);
        const response = await fetch(`http://localhost:5000/empleados/comunas/${regionId}`);
        if (!response.ok) throw new Error('Error al cargar comunas');
        const comunas = await response.json();
        
        // Almacenar las comunas para esta región
        comunasPorRegion.set(parseInt(regionId), comunas);
        
        const select = document.getElementById('comuna-select');
        select.innerHTML = '<option value="">Seleccione una comuna</option>';
        select.disabled = false;
        
        comunas.forEach(comuna => {
            const option = document.createElement('option');
            option.value = comuna.id;
            option.textContent = comuna.nombre;
            select.appendChild(option);
        });
        
        console.log('Comunas cargadas:', comunas);
    } catch (error) {
        console.error('Error cargando comunas:', error);
        alert('Error al cargar las comunas');
    }
}

// Función para validar la relación región-comuna
function validarRegionComuna(regionId, comunaId) {
    console.log('Validando región:', regionId, 'comuna:', comunaId);
    
    if (!regionId || !comunaId) {
        throw new Error('Debe seleccionar tanto la región como la comuna');
    }

    const regionIdNum = parseInt(regionId);
    const comunaIdNum = parseInt(comunaId);
    
    // Obtener las comunas almacenadas para esta región
    const comunas = comunasPorRegion.get(regionIdNum);
    
    if (!comunas) {
        throw new Error('No se encontraron comunas para la región seleccionada');
    }
    
    // Verificar si la comuna pertenece a la región
    const comunaValida = comunas.some(comuna => comuna.id === comunaIdNum);
    
    if (!comunaValida) {
        throw new Error('La comuna seleccionada no pertenece a la región');
    }
    
    return true;
}

// Renderizar tabla
function renderTable(page) {
    console.log('Renderizando tabla para página:', page);
    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    const rows = data.slice(startIndex, endIndex);

    const tableBody = document.querySelector("#data-table tbody");
    tableBody.innerHTML = "";

    rows.forEach(row => {
        const tr = document.createElement("tr");
        tr.setAttribute('data-id', row.ID);
        tr.innerHTML = `
            <td>${row.Nombre_Completo}</td>
            <td>${row.RUT}</td>
            <td>${row.Sexo}</td>
            <td>${row.Teléfono || ''}</td>
            <td>${row.email}</td>
            <td>${row.Tipo_Usuario}</td>
            <td>${row.Estado || 'N/A'}</td>
        `;
        tr.addEventListener('click', () => selectRow(tr));
        tableBody.appendChild(tr);
    });
}

// Renderizar paginación
function renderPagination() {
    const totalPages = Math.ceil(data.length / rowsPerPage);
    const pagination = document.querySelector("#pagination");
    pagination.innerHTML = "";

    // Botón Anterior
    const prevButton = document.createElement("button");
    prevButton.textContent = "Anterior";
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(prevButton);

    // Botones de página
    for (let i = 1; i <= totalPages; i++) {
        const button = document.createElement("button");
        button.textContent = i;
        button.classList.toggle("active", i === currentPage);
        button.onclick = () => {
            currentPage = i;
            renderTable(currentPage);
            renderPagination();
        };
        pagination.appendChild(button);
    }

    // Botón Siguiente
    const nextButton = document.createElement("button");
    nextButton.textContent = "Siguiente";
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTable(currentPage);
            renderPagination();
        }
    };
    pagination.appendChild(nextButton);
}

// Seleccionar fila
function selectRow(tr) {
    document.querySelectorAll('#data-table tbody tr').forEach(row => {
        row.classList.remove('selected');
    });
    tr.classList.add('selected');
    currentEmployeeId = tr.getAttribute('data-id');
    
    document.getElementById('editEmpleado').disabled = false;
    document.getElementById('deleteEmpleado').disabled = false;
}

// Recopilar datos del formulario
async function gatherFormData() {
    console.log('Recopilando datos del formulario...');
    try {
        const tipoUsuario = document.querySelector("input[name='empleo']:checked");
        if (!tipoUsuario) {
            throw new Error('Debe seleccionar un tipo de usuario');
        }

        const sexo = document.querySelector("input[name='sexo']:checked");
        if (!sexo) {
            throw new Error('Debe seleccionar un sexo');
        }

        const regionId = document.getElementById('region-select').value;
        const comunaId = document.getElementById('comuna-select').value;

        // Validar relación región-comuna antes de continuar
        validarRegionComuna(regionId, comunaId);

        const formData = {
            tipo_usuario: tipoUsuario.value,
            sexo: sexo.value,
            nombre_completo: document.querySelector("input[name='nombreCompleto']").value.trim(),
            email: document.querySelector("input[name='email']").value.trim(),
            fecha_nacimiento: document.querySelector("input[name='fechaNacimiento']").value,
            rut: document.querySelector("input[name='rut']").value.trim(),
            telefono: document.querySelector("input[name='telefono']").value.trim(),
            numero_casa: document.querySelector("input[name='numeroCasa']").value.trim(),
            
            direccion: {
                ciudad: document.querySelector("input[name='ciudad']").value.trim(),
                codigo_postal: document.querySelector("input[name='codigoPostal']").value.trim(),
                region_id: regionId,
                comuna_id: comunaId
            },
            
            nombre_usuario: document.querySelector("input[name='nombreUsuario']").value.trim(),
            contrasena: document.querySelector("input[name='contrasena']").value,
            estado: document.querySelector("select[name='estado']").value,
            cargo: document.querySelector("input[name='cargo']").value.trim(),
            
            permisos: getPermissionsData()
        };

        return formData;
    } catch (error) {
        console.error('Error en gatherFormData:', error);
        throw error;
    }
}

// Obtener datos de permisos
function getPermissionsData() {
    return {
        dashboard: {
            ver_metricas_generales: document.querySelector("input[data-permission='dashboard-ver-metricas-generales']").checked,
            ver_metricas_detalladas: document.querySelector("input[data-permission='dashboard-ver-metricas-detalladas']").checked,
            exportar_datos: document.querySelector("input[data-permission='dashboard-exportar-datos']").checked,
            personalizar_vistas: document.querySelector("input[data-permission='dashboard-personalizar-vistas']").checked
        },
        inventario: {
            ver_inventario: document.querySelector("input[data-permission='inventario-ver']").checked,
            agregar_productos: document.querySelector("input[data-permission='inventario-agregar']").checked,
            modificar_productos: document.querySelector("input[data-permission='inventario-modificar']").checked,
            eliminar_productos: document.querySelector("input[data-permission='inventario-eliminar']").checked,
            ajustar_stock: document.querySelector("input[data-permission='inventario-ajustar']").checked
        },
        empleados: {
            ver_empleados: document.querySelector("input[data-permission='empleados-ver']").checked,
            agregar_empleados: document.querySelector("input[data-permission='empleados-agregar']").checked,
            modificar_empleados: document.querySelector("input[data-permission='empleados-modificar']").checked,
            eliminar_empleados: document.querySelector("input[data-permission='empleados-eliminar']").checked
        },
        reportes: {
            ver_reportes: document.querySelector("input[data-permission='reportes-ver']").checked,
            generar_reportes: document.querySelector("input[data-permission='reportes-generar']").checked,
            exportar_reportes: document.querySelector("input[data-permission='reportes-exportar']").checked
        }
    };
}

// Guardar nuevo empleado
async function saveNewEmpleado() {
    console.log('Iniciando guardado de empleado...');
    try {
        const formData = await gatherFormData();
        
        if (!editMode) {
            const confirmarContrasena = document.querySelector("input[name='confirmarContrasena']").value;
            if (!formData.contrasena) {
                throw new Error('La contraseña es obligatoria');
            }
            if (formData.contrasena !== confirmarContrasena) {
                throw new Error('Las contraseñas no coinciden');
            }
            if (formData.contrasena.length < 6) {
                throw new Error('La contraseña debe tener al menos 6 caracteres');
            }
        }

        const url = editMode ? 
            `http://localhost:5000/empleados/actualizar/${currentEmployeeId}` :
            'http://localhost:5000/empleados/guardar';
        
        const method = editMode ? 'PUT' : 'POST';
        
        console.log(`Enviando petición ${method} a ${url}`);
        console.log('Datos a enviar:', formData);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();
        console.log('Respuesta del servidor:', result);

        if (!response.ok) {
            throw new Error(result.error || `Error del servidor: ${response.status}`);
        }

        if (!result.success) {
            throw new Error(result.error || 'Error desconocido al guardar el empleado');
        }

        alert(editMode ? 'Empleado actualizado correctamente' : 'Empleado guardado correctamente');
        closePopup();
        await fetchData();

    } catch (error) {
        console.error('Error en saveNewEmpleado:', error);
        alert(error.message);
    }
}

// Funciones de manejo del popup
function openPopup(mode = 'new') {
    editMode = mode === 'edit';
    document.getElementById('popup').style.display = 'block';
    document.querySelector('.popup-title').textContent = editMode ? 'Editar Empleado' : 'Nuevo Empleado';
    
    if (editMode && currentEmployeeId) {
        loadEmployeeData(currentEmployeeId);
    } else {
        resetForm();
    }
}

function closePopup() {
    document.getElementById('popup').style.display = 'none';
    resetForm();
    editMode = false;
    currentEmployeeId = null;
}

function resetForm() {
    document.querySelector('form').reset();
    document.querySelector('.tab button').click();
    const comunaSelect = document.getElementById('comuna-select');
    comunaSelect.innerHTML = '<option value="">Seleccione una comuna</option>';
    comunaSelect.disabled = true;
}

// Manejador de pestañas
function openTab(evt, tabName) {
    const tabcontent = document.getElementsByClassName("tabcontent");
    for (let i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    const tablinks = document.getElementsByClassName("tablinks");
    for (let i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}

// Cargar datos de empleado para edición
async function loadEmployeeData(employeeId) {
    try {
        console.log('Cargando datos del empleado:', employeeId);
        const response = await fetch(`http://localhost:5000/empleados/obtener/${employeeId}`);
        
        if (!response.ok) {
            throw new Error('Error al obtener datos del empleado');
        }

        const result = await response.json();
        if (!result.success) {
            throw new Error(result.error);
        }

        const empleado = result.data;
        console.log('Datos recibidos del empleado:', empleado);

        // Llenar datos básicos
        const tipoUsuarioInput = document.querySelector(`input[name='empleo'][value='${empleado.tipo_usuario}']`);
        if (tipoUsuarioInput) tipoUsuarioInput.checked = true;

        const sexoInput = document.querySelector(`input[name='sexo'][value='${empleado.sexo}']`);
        if (sexoInput) sexoInput.checked = true;

        // Formatear la fecha al formato yyyy-MM-dd
        const fecha = new Date(empleado.fecha_nacimiento);
        const fechaFormateada = fecha.toISOString().split('T')[0];

        // Llenar los campos del formulario
        const campos = {
            'nombreCompleto': empleado.nombre_completo,
            'fechaNacimiento': fechaFormateada,
            'rut': empleado.rut,
            'telefono': empleado.telefono || '',
            'email': empleado.email,
            'numeroCasa': empleado.numero_casa || '',
            'ciudad': empleado.ciudad || '',
            'codigoPostal': empleado.codigo_postal || '',
            'nombreUsuario': empleado.nombre_usuario || '',
            'cargo': empleado.cargo || ''
        };

        // Llenar cada campo
        for (const [campo, valor] of Object.entries(campos)) {
            const elemento = document.querySelector(`input[name='${campo}']`);
            if (elemento) elemento.value = valor;
        }

        // Manejar estado
        const estadoSelect = document.querySelector("select[name='estado']");
        if (estadoSelect) estadoSelect.value = empleado.estado || 'Activo';

        // Cargar región y comuna
        if (empleado.region_id) {
            const regionSelect = document.querySelector("#region-select");
            regionSelect.value = empleado.region_id;
            await loadComunas(empleado.region_id);
            
            if (empleado.comuna_id) {
                const comunaSelect = document.querySelector("#comuna-select");
                comunaSelect.value = empleado.comuna_id;
                comunaSelect.disabled = false;
            }
        }

        // Deshabilitar campos de contraseña en modo edición
        const contrasenaInput = document.querySelector("input[name='contrasena']");
        const confirmarContrasenaInput = document.querySelector("input[name='confirmarContrasena']");
        if (contrasenaInput) contrasenaInput.required = false;
        if (confirmarContrasenaInput) confirmarContrasenaInput.required = false;

        console.log('Datos del empleado cargados correctamente');
    } catch (error) {
        console.error('Error cargando datos del empleado:', error);
        alert('Error al cargar los datos del empleado: ' + error.message);
    }
}

// Eliminar empleado
async function deleteEmployee() {
    if (!currentEmployeeId) {
        alert('Seleccione un empleado para eliminar');
        return;
    }

    if (!confirm('¿Está seguro que desea eliminar este empleado?')) {
        return;
    }

    try {
        const response = await fetch(`http://localhost:5000/empleados/eliminar/${currentEmployeeId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Error al eliminar el empleado');
        }

        const result = await response.json();
        
        if (result.success) {
            alert('Empleado eliminado correctamente');
            currentEmployeeId = null;
            document.getElementById('editEmpleado').disabled = true;
            document.getElementById('deleteEmpleado').disabled = true;
            await fetchData();
        } else {
            throw new Error(result.error || 'Error al eliminar el empleado');
        }
    } catch (error) {
        console.error('Error eliminando empleado:', error);
        alert(error.message);
    }
}

// Event Listeners e Inicialización
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando página...');
    
    // Cargar datos iniciales
    fetchData();
    loadRegiones();
    
    // Configurar botones principales
    document.getElementById('newEmpleado').addEventListener('click', () => openPopup('new'));
    document.getElementById('editEmpleado').addEventListener('click', () => openPopup('edit'));
    document.getElementById('deleteEmpleado').addEventListener('click', deleteEmployee);

    // Configurar modal
    document.querySelector('.close-button').addEventListener('click', closePopup);
    document.querySelector('.cancel').addEventListener('click', closePopup);
    document.querySelector('form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveNewEmpleado();
    });

    // Event listener para cambio de región
    document.getElementById('region-select').addEventListener('change', function(e) {
        const regionId = e.target.value;
        const comunaSelect = document.getElementById('comuna-select');
        
        if (regionId) {
            loadComunas(regionId);
        } else {
            comunaSelect.innerHTML = '<option value="">Seleccione una comuna</option>';
            comunaSelect.disabled = true;
        }
    });

    // Configurar eventos de las pestañas
    document.querySelectorAll('.tab button').forEach(button => {
        button.addEventListener('click', (e) => openTab(e, e.target.getAttribute('data-tab')));
    });

    // Abrir primera pestaña por defecto
    document.querySelector('.tab button').click();
});