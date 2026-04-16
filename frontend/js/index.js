   async function loadProducts() {
      const errorMsg = document.getElementById('errorMsg');
      const tbody = document.getElementById('productTable');

      try {
        const res = await apiFetch('/products/');

        if (!res.ok) throw new Error('Error al cargar los productos');

        const products = await res.json();

        if (products.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="5" class="px-6 py-6 text-center text-gray-400">No hay productos</td>
            </tr>`;
          return;
        }

        tbody.innerHTML = products.map(p => `
          <tr class="hover:bg-gray-50 cursor-pointer" onclick="window.location='product.html?id=${p.id}'">
            <td class="px-6 py-4 font-medium text-gray-800">${p.name}</td>
            <td class="px-6 py-4 text-gray-600">${p.unit}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 rounded-full text-xs font-semibold ${p.stock === 0 ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-700'}">
                ${p.stock}
              </span>
            </td>
            <td class="px-6 py-4 text-gray-600">$${p.purchase_price}</td>
            <td class="px-6 py-4 text-gray-600">$${p.sale_price}</td>
          </tr>
        `).join('');

      } catch (err) {
        errorMsg.textContent = err.message;
        errorMsg.classList.remove('hidden');
        tbody.innerHTML = '';
      }
    }

    loadProducts();