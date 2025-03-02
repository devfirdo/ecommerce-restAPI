# E-commerce API

A RESTful API for an e-commerce platform that allows users to browse and purchase products, while admins manage the system efficiently.

---

## 📌 Features

### 🛍️ User Features
- **Authentication & Profile Management**  
  ✅ User Registration (JWT-based authentication)  
  ✅ Login & Logout with JWT Token  
  ✅ Retrieve & Update user profile information  

- **Product Browsing & Searching**  
  ✅ View list of all available products  
  ✅ Filter products by category  
  ✅ Search for products by name or description  
  ✅ View product details  

- **Shopping Cart**  
  ✅ Add products to the cart  
  ✅ Update product quantity in the cart  
  ✅ Remove products from the cart  
  ✅ View cart items & total price  

- **Order Management**  
  ✅ Place an order from the cart  
  ✅ View order history with order details  
  ✅ Track order status (Pending, Shipped, Delivered)  

- **Product Reviews & Ratings**  
  ✅ Leave a review & rating for purchased products  
  ✅ View ratings & reviews for products  

### 🛠️ Admin Features
- **User Management**  
  ✅ View all registered users  
  ✅ Block or delete users (if necessary)  

- **Product Management**  
  ✅ Create new products with images, price, and category  
  ✅ Update product details  
  ✅ Delete products (soft delete recommended)  
  ✅ Manage product categories  

- **Order Management**  
  ✅ View all orders placed by users  
  ✅ Update order status (Pending, Shipped, Delivered)  
  ✅ Cancel orders if necessary  

---

## 🏗️ Tech Stack

- **Backend:** Django, Django REST Framework (DRF)  
- **Database:** PostgreSQL  
- **Authentication:** JWT (SimpleJWT)  
- **API Testing & Documentation:** Postman  

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-username/ecommerce-api.git
cd ecommerce-api


2️⃣ Create and Activate Virtual Environment
```sh
python -m venv venv
..\..\venv\Scripts\activate  

3️⃣ Install Dependencies

pip install -r requirements.txt

5️⃣ Apply Migrations

python manage.py makemigrations
python manage.py migrate

6️⃣ Create Superuser (Admin Access)

python manage.py createsuperuser

7️⃣ Run the Server

python manage.py runserver

8️⃣ Access the API

http://127.0.0.1:8000/api/v1/


🔥 API Documentation
The API is documented using Postman.

📂 Postman Collection
You can import the Postman collection provided in E-Commerce Testing.postman_collection.json to test the API endpoints.

📌 Base URL
http://127.0.0.1:8000/api/v1/

🛠 Authentication
Register User → POST /auth/register/
Login User → POST /auth/login/
Logout User → POST /auth/logout/
Refresh Token → POST /auth/token/refresh/


🏪 Product & Category Management
List Categories → GET /core/categories/
Create Category (Admin) → POST /core/categories/
Update Category (Admin) → PATCH /core/categories/{id}/
Delete Category (Admin) → DELETE /core/categories/{id}/
List Products → GET /core/products/
List Single Product →  Get /core/products/{id}
Create Product (Admin) → POST /core/products/
Update Product (Admin) → PATCH /core/products/{id}/
Delete Product (Admin) → DELETE /core/products/{id}/
Filter Products by Category → GET /core/products/?category={category_id}
Filter products by name/description → GET /core/products/?search={product_name}

🛒 Shopping Cart
View Cart → GET /core/cart/
Add to Cart → POST /core/cart/
Update Cart Item → PATCH /core/cart/{cart_id}/
Remove from Cart → DELETE /core/cart/{cart_id}/

📦 Orders
Place Order → POST /core/orders/place/
View Order History → GET /core/orders/
Track Order Status → GET /core/orders/{order_id}/status/
View All Orders (Admin) → GET /core/orders/all/
Update Order Status (Admin) → PATCH /core/orders/{order_id}/update-status/
Cancel Order (Admin) → PATCH /core/orders/{order_id}/cancel/


📝 Reviews
View Product Reviews → GET /core/products/{product_id}/reviews/
Add Review → POST /core/products/{product_id}/reviews/

👥 User Management (Admin)
View All Users → GET /core/users/
Block User → PATCH /core/users/{user_id}/block/
Delete User → DELETE /core/users/{user_id}/delete/


👥 User Management (Users)
View User Profile → GET /auth/profile/
Update User Profile → PUT /auth/profile/update/

🔑 Authentication & Security
Uses JWT for authentication (access and refresh tokens).
Refresh token must be included when logging out.
Admin endpoints require an admin account.


## 🔧 Postman Environment Variables

To simplify authentication in Postman, the following environment variables are used:

1️⃣ **`user_token`**  
   - Stores the **access token** generated when a regular user logs in.  
   - Used for user-related API requests (e.g., adding to cart, placing orders).  

2️⃣ **`admin_token`**  
   - Stores the **access token** generated when an admin logs in.  
   - Used for admin-only API requests (e.g., managing products, users, and orders).  

3️⃣ **`logout_token`**  
   - Stores the **refresh token** generated during login.  
   - Used to **log out** a user by sending the refresh token.  

### 🔹 How to Use These Variables in Postman?
- **Login as User** → The response will automatically save the access token in `user_token`.  
- **Login as Admin** → The response will automatically save the access token in `admin_token`.  
- **Logout** → The stored `logout_token` will be used in the logout request.


🏗 Tech Stack
Backend: Django, Django REST Framework
Database: PostgreSQL
Authentication: JWT (SimpleJWT)
API Testing: Postman

📜 License
This project is licensed under the MIT License.

📩 Contact
For any queries, reach out to:

Email: firdo.tech.dev@gmail.com
GitHub: devfirdo