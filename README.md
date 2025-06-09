# 🍽️ Zomato Restaurant Order Analysis using SQL

## 📌 Project Overview
This project analyzes Zomato’s restaurant order data using SQL to uncover:
- Customer preferences and top menu items
- Peak order times and regional sales trends
- Restaurant and cuisine performance metrics
- Revenue generation and customer behavior

The goal is to derive **actionable business insights** through structured queries and data analysis.

---

## 🛠️ Tools & Technologies
- **PostgreSQL** – for writing and executing SQL queries
- **Microsoft Excel** – for data exploration and formatting
- **CSV Files** – as the data source

---

## 📊 Focus Areas
- Order volume and timing
- Most ordered cuisines and items
- Revenue and sales patterns
- Cuisine and restaurant performance by region
- Top customers by order frequency and spend

---

## 🧾 Dataset Summary
- `orders.csv` – order_id, order_date, order_time, customer_id, city_id  
- `order_details.csv` – order_id, menu_item_id, quantity, price  
- `menu_items.csv` – menu_item_id, item_name, cuisine_type, price  
- `customers.csv` – customer_id, name, age, gender, city_id  
- `restaurants.csv` – restaurant_id, restaurant_name, city_id, rating  
- `cities.csv` – city_id, city_name, state, region  

---

## ✅ Basic SQL Analysis
- Total Orders Placed: `COUNT(*)`
- Total Revenue: `SUM(quantity * price)`
- Highest Priced Menu Item: `ORDER BY price DESC LIMIT 1`
- Most Common Cuisine: `GROUP BY cuisine_type`
- Top 5 Menu Items: `ORDER BY SUM(quantity) DESC LIMIT 5`

---

## ⚙️ Intermediate SQL Analysis
- Average Order Value per Customer
- Orders by City and Restaurant
- Orders by Day of Week and Month: `EXTRACT()`
- Repeat vs New Customer Orders: `HAVING COUNT(order_id) > 1`
- Top 3 Cuisines by Revenue

---

## 📈 Advanced SQL Analysis
- % Revenue Contribution by Cuisine
- Cumulative Revenue Over Time: `OVER(ORDER BY date)`
- Top Menu Items per Cuisine: `RANK() OVER (PARTITION BY ...)`
- Customer Cohort Analysis (by first order month)
- Peak Order Hours by City/Region: `EXTRACT(HOUR FROM order_time)`

---

## 📥 How to Use
1. Load the CSV files into PostgreSQL tables.
2. Run the provided SQL queries from the presentation file (`SQL PROJECT PPT.pdf`).
3. Analyze the outputs and use visual tools (Excel/Power BI/Tableau) for dashboards.

---

## 👤 Author
**Allapu Srivarshan**  
Aspiring Data Analyst  
📧 Email: allapusrivarshan6@gmail.com

> “SQL projects highlight a data analyst’s proficiency in retrieving, transforming, and analyzing data from real-world databases, demonstrating their ability to generate actionable insights through structured queries and analytical thinking.”

---

## 📎 Files Included
- SQL PROJECT PPT.pdf (Presentation of SQL queries and insights)

