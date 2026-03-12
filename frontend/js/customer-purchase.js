// Customer Purchase Module
// Handles customer buying products

function showBuyModal(barcode, productName, price) {
     console.log('Show buy modal for:', barcode, productName, price);
     
     const modalContainer = document.getElementById('modalContainer');
     if (!modalContainer) {
         alert('Modal container not found!');
         return;
     }
     
     modalContainer.innerHTML = `
         <div class="modal active">
             <div class="modal-content">
                 <div class="modal-header">
                     <h3>Buy Product</h3>
                     <button class="modal-close" onclick="closeModal()">&times;</button>
                 </div>
                 <form id="buyForm" onsubmit="submitPurchase(event, '${barcode}')">
                     <div class="form-group">
                         <label>Product Name</label>
                         <input type="text" value="${productName}" disabled>
                     </div>
                     <div class="form-group">
                         <label>Price per Unit (Rs)</label>
                         <input type="number" value="${price}" disabled>
                     </div>
                     <div class="form-group">
                         <label>Quantity *</label>
                         <input type="number" name="quantity" min="1" value="1" required>
                     </div>
                     <div class="form-group">
                         <label>Payment Method *</label>
                         <select name="payment_method" required>
                             <option value="cash">Cash</option>
                             <option value="card">Card</option>
                             <option value="online">Online</option>
                         </select>
                     </div>
                     <div style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                         <p style="margin: 0;">
                             <strong>Total Amount: Rs</strong>
                             <span id="totalAmount">${(price * 1).toFixed(2)}</span>
                         </p>
                     </div>
                     <button type="submit" class="btn btn-primary" style="width: 100%; margin-top: 20px;">Proceed to Buy</button>
                 </form>
             </div>
         </div>
     `;
     
     // Add event listener to update total amount when quantity changes
     const quantityInput = document.querySelector('input[name="quantity"]');
     if (quantityInput) {
         quantityInput.addEventListener('change', () => {
             const qty = parseInt(quantityInput.value) || 1;
             const total = (price * qty).toFixed(2);
             const totalAmountSpan = document.getElementById('totalAmount');
             if (totalAmountSpan) {
                 totalAmountSpan.textContent = total;
             }
         });
         quantityInput.addEventListener('input', () => {
             const qty = parseInt(quantityInput.value) || 1;
             const total = (price * qty).toFixed(2);
             const totalAmountSpan = document.getElementById('totalAmount');
             if (totalAmountSpan) {
                 totalAmountSpan.textContent = total;
             }
         });
     }
 }

async function submitPurchase(event, barcode) {
     event.preventDefault();
     const form = event.target;
     const formData = new FormData(form);
     const quantity = parseInt(formData.get('quantity'));
     const payment_method = formData.get('payment_method');
     
     if (quantity < 1) {
         alert('Quantity must be at least 1');
         return;
     }
     
     console.log('Submitting purchase:', { barcode, quantity, payment_method });
     
     try {
         const response = await fetch(`${API_URL}/sales/customer-purchase/`, {
             method: 'POST',
             headers: getAuthHeaders(),
             body: JSON.stringify({
                 barcode: barcode,
                 quantity: quantity,
                 payment_method: payment_method
             })
         });
         
         console.log('Purchase response status:', response.status);
         const result = await response.json();
         console.log('Purchase response:', result);
         
         if (response.ok && result.success) {
             const saleDetails = result.sale || {};
             alert(`✅ Purchase Successful!\n\nProduct: ${saleDetails.product_name}\nQuantity: ${saleDetails.quantity}\nTotal Amount: Rs${saleDetails.total_amount}\nDiscount Saved: Rs${saleDetails.discount_saved || 0}`);
             closeModal();
             loadProducts();
         } else {
             const errorMsg = result.error || result.message || 'Unknown error occurred';
             alert(`Error: ${errorMsg}`);
         }
     } catch (error) {
         console.error('Purchase error:', error);
         alert(`Error processing purchase: ${error.message}`);
     }
 }
