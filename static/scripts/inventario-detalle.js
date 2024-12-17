document.addEventListener('DOMContentLoaded', function() {
    // Obtener el ID del producto de la URL
    const urlParams = new URLSearchParams(window.location.search);
    const productoId = urlParams.get('id');
    
    if (productoId) {
        loadProductoDetails(productoId);
    } else {
        showError('No se especificó un producto');
        setTimeout(() => window.history.back(), 2000);
    }
});

async function loadProductoDetails(productoId) {
    try {
        const response = await fetch(`/api/inventario/producto/${productoId}`);
        if (!response.ok) throw new Error('Error al cargar los datos del producto');
        
        const data = await response.json();
        renderProductoDetails(data.info_producto);
        renderOrdenes(data.ordenes);
        
    } catch (error) {
        console.error('Error:', error);
        showError('Error al cargar los detalles del producto');
    }
}

function renderProductoDetails(info) {
    // Información Principal
    document.getElementById('codigo').textContent = info.codigo;
    document.getElementById('nombre').textContent = info.nombre;
    document.getElementById('tipo_prenda').textContent = info.tipo_prenda;
    document.getElementById('estado').textContent = info.estado;
    
    // Stock
    document.getElementById('stock_actual').textContent = info.stock_actual;
    document.getElementById('stock_minimo').textContent = info.stock_minimo;
    
    // Evaluar estado del stock
    const stockStatus = document.getElementById('stock_status');
    if (info.stock_actual <= info.stock_minimo) {
        stockStatus.textContent = '⚠️ Stock bajo';
        stockStatus.classList.add('warning');
    } else {
        stockStatus.textContent = '✅ Stock normal';
        stockStatus.classList.add('normal');
    }
    
    // Precios
    document.getElementById('valor_compra').textContent = formatCurrency(info.valor_compra);
    document.getElementById('valor_venta').textContent = formatCurrency(info.valor_venta);
    
    // Calcular y mostrar margen
    const margen = ((info.valor_venta - info.valor_compra) / info.valor_compra * 100).toFixed(2);
    document.getElementById('margen').textContent = `${margen}%`;
    
    // Características
    document.getElementById('marca').textContent = info.marca || 'No especificado';
    document.getElementById('talla').textContent = info.talla || 'No especificado';
    document.getElementById('color').textContent = info.color || 'No especificado';
    
    // Descripción
    document.getElementById('descripcion').textContent = info.descripcion || 'Sin descripción';
}

function renderOrdenes(ordenes) {
    const tbody = document.querySelector('#ordenes-table tbody');
    tbody.innerHTML = '';
    
    if (!ordenes || ordenes.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="6" class="text-center">No hay órdenes registradas</td>';
        tbody.appendChild(tr);
        return;
    }
    
    ordenes.forEach(orden => {
        const tr = document.createElement('tr');
        const total = orden.cantidad * orden.precio_unitario;
        
        tr.innerHTML = `
            <td>${orden.fecha}</td>
            <td>${orden.tipo}</td>
            <td>${orden.estado}</td>
            <td>${orden.cantidad}</td>
            <td>${formatCurrency(orden.precio_unitario)}</td>
            <td>${formatCurrency(total)}</td>
        `;
        
        tbody.appendChild(tr);
    });
}

function formatCurrency(value) {
    return new Intl.NumberFormat('es-CL', {
        style: 'currency',
        currency: 'CLP'
    }).format(value);
}

function showError(message) {
    alert('❌ ' + message);
}