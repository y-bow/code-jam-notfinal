# Student Portal - Internship Listings

A purely frontend web application designed for a student portal, allowing students to search and filter through internship opportunities, and an admin interface for creating, editing, and deleting listings.

## Project Structure
- `frontend/`: Contains HTML, CSS, and JS files for the Student Portal and Admin Dashboard.

---

## 🏗️ Example UI Layout & Strategy
- **Student View (`index.html`)**: A search bar at the top with two filter dropdowns (Location, Duration). Below is a dynamic grid of glassmorphic internship cards displaying Company Name, Role Title, Location badge, Duration, Deadline, and Stipend. A "View Details" button opens a modal with full requirements and a dummy "Apply" action.
- **Admin View (`admin.html`)**: Tabular list of internships containing action buttons (`Edit` and `Delete`). A primary "Add New Internship" button floats at the top. Forms open in a modern modal.

---

## 🗄️ Data Storage

This application operates entirely in the browser without any backend API.
- All internship listings are saved locally to your browser using `localStorage`.
- On the first load, the app is automatically seeded with 4 sample internships.
- Any changes made in the Admin Dashboard (add, edit, delete) are saved locally and immediately reflected in the Student Portal.

---

## 🚀 How to Run Locally

Since this is purely HTML/CSS/JS, no servers or installation are required!

1. Open `frontend/index.html` in your web browser to view the Student Portal.
2. Open `frontend/admin.html` in your web browser to view the Admin Dashboard and manage entries.

*(Optional: Use an extension like Live Server in VSCode for auto-reloading during development.)*
