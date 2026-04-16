const params = new URLSearchParams(window.location.search);
    const productId = params.get('id');
    if (!productId) window.location.href = 'index.html';

    async function loadProduct() {
      const errorMsg = document.getElementById('errorMsg');
      try {
        const res = await apiFetch(`/products/${productId}`);
        if (!res.ok) throw new Error('Producto no encontrado');
        const p = await res.json();

        document.getElementById('productName').textContent = p.name;
        document.getElementById('productUnit').textContent = p.unit;
        document.getElementById('productStock').textContent = p.stock;
        document.getElementById('productPurchase').textContent = `$${p.purchase_price}`;
        document.getElementById('productSale').textContent = `$${p.sale_price}`;
        document.getElementById('editBtn').href = `edit_product.html?id=${p.id}`;
        document.getElementById('productCard').classList.remove('hidden');

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      }
    }

    async function loadMovements() {
      const tbody = document.getElementById('movementsTable');
      try {
        const res = await apiFetch(`/products/${productId}/movements`);

        if (!res.ok) throw new Error('Error al cargar movimientos');

        const movements = await res.json();

        if (movements.length === 0) {
          tbody.innerHTML = `<tr><td colspan="3" class="px-6 py-6 text-center text-gray-400">Sin movimientos</td></tr>`;
          return;
        }

        tbody.innerHTML = movements.map(m => {
          const esIngreso = m.quantity > 0;
          const fecha = new Date(m.created_at).toLocaleString('es-AR');
          return `
            <tr class="hover:bg-gray-50">
              <td class="px-6 py-4 text-gray-600">${fecha}</td>
              <td class="px-6 py-4">
                <span class="px-2 py-1 rounded-full text-xs font-semibold ${esIngreso ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}">
                  ${esIngreso ? 'Ingreso' : 'Retiro'}
                </span>
              </td>
              <td class="px-6 py-4 font-medium ${esIngreso ? 'text-green-700' : 'text-red-600'}">
                ${esIngreso ? '+' : ''}${m.quantity}
              </td>
            </tr>`;
        }).join('');

      } catch (err) {
        tbody.innerHTML = `<tr><td colspan="3" class="px-6 py-6 text-center text-red-400">${err.message}</td></tr>`;
      }
    }

    document.getElementById('deleteBtn').addEventListener('click', async () => {
      if (!confirm('¿Eliminar este producto?')) return;

      try {
        const res = await apiFetch(`/products/${productId}`, { method: 'DELETE' });

        if (!res.ok) throw new Error('Error al eliminar el producto');

        window.location.href = 'index.html';

      } catch (err) {
        const errorMsg = document.getElementById('errorMsg');
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
      }
    });

    loadProduct();
    loadMovements();