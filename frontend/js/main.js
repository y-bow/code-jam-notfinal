// Sample Data
const sampleInternships = [
    {
        id: 1,
        company_name: "TechNova Solutions",
        role: "Software Developer Intern",
        location: "Remote",
        duration: "3 months",
        stipend: "$2,500/month",
        deadline: "2024-06-15",
        description: "Join our dynamic engineering team to build scalable web applications. You will be working with React on the frontend and Node.js on the backend.",
        requirements: "Proficiency in JavaScript, HTML, CSS. Familiarity with React or similar frameworks. Strong problem-solving skills."
    },
    {
        id: 2,
        company_name: "MarketMinds Group",
        role: "Marketing Intern",
        location: "On-site",
        duration: "6 months",
        stipend: "$1,800/month",
        deadline: "2024-05-30",
        description: "Help craft compelling digital campaigns and manage SEO initiatives across our flagship brands. Great opportunity for hands-on experience.",
        requirements: "Excellent written communication. Understanding of digital marketing platforms. Creative mindset."
    },
    {
        id: 3,
        company_name: "DataSphere Analytics",
        role: "Data Science Intern",
        location: "Hybrid",
        duration: "4 months",
        stipend: "$3,000/month",
        deadline: "2024-07-01",
        description: "Work with vast datasets to uncover insights and build predictive models using machine learning techniques.",
        requirements: "Strong Python and SQL skills. Knowledge of Pandas, Scikit-Learn. Background in statistics."
    },
    {
        id: 4,
        company_name: "CloudNine Designs",
        role: "UX/UI Design Intern",
        location: "Remote",
        duration: "3 months",
        stipend: "$2,000/month",
        deadline: "2024-08-15",
        description: "Collaborate with senior designers to create intuitive and beautiful user interfaces for mobile and web applications.",
        requirements: "Portfolio showcasing design skills. Proficiency in Figma or Adobe XD."
    }
];

// DOM Elements
const internshipsContainer = document.getElementById('internshipsContainer');
const searchRole = document.getElementById('searchRole');
const filterLocation = document.getElementById('filterLocation');
const filterDuration = document.getElementById('filterDuration');

const modal = document.getElementById('detailsModal');
const closeModalBtn = document.getElementById('closeModalBtn');

// Global state for internships
let internships = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize LocalStorage if empty
    if (!localStorage.getItem('internships')) {
        localStorage.setItem('internships', JSON.stringify(sampleInternships));
    }
    
    fetchInternships();

    // Event Listeners for Filters
    searchRole.addEventListener('input', fetchInternships);
    filterLocation.addEventListener('change', fetchInternships);
    filterDuration.addEventListener('change', fetchInternships);

    // Modal Close Events
    closeModalBtn.addEventListener('click', () => modal.classList.remove('active'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// Fetch data from LocalStorage
function fetchInternships() {
    internshipsContainer.innerHTML = '<div class="loader"><i class="fas fa-circle-notch fa-spin"></i> Loading internships...</div>';
    
    setTimeout(() => {
        try {
            const data = JSON.parse(localStorage.getItem('internships')) || [];
            
            // Apply Filters Client-Side
            const roleQuery = searchRole.value.toLowerCase();
            const locQuery = filterLocation.value;
            const durQuery = filterDuration.value;
            
            internships = data.filter(intern => {
                const matchesRole = intern.role.toLowerCase().includes(roleQuery);
                const matchesLoc = locQuery ? intern.location === locQuery : true;
                const matchesDur = durQuery ? intern.duration === durQuery : true;
                return matchesRole && matchesLoc && matchesDur;
            });
            
            renderInternships();
        } catch (error) {
            console.error('Error fetching internships:', error);
            internshipsContainer.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-exclamation-circle" style="color: #ef4444;"></i>
                    <h3>Failed to load data</h3>
                    <p>Error reading from local storage.</p>
                </div>
            `;
        }
    }, 300); // Small timeout to simulate loading state for UX
}

// Render the grid
function renderInternships() {
    if (internships.length === 0) {
        internshipsContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <h3>No internships found</h3>
                <p>Try adjusting your search criteria.</p>
            </div>
        `;
        return;
    }

    internshipsContainer.innerHTML = internships.map(intern => `
        <div class="internship-card">
            <div class="card-header">
                <div>
                    <div class="company-name">${intern.company_name}</div>
                    <div class="role-title">${intern.role}</div>
                </div>
                <span class="badge">${intern.location}</span>
            </div>
            <div class="card-body">
                <div class="detail-item">
                    <i class="fas fa-clock"></i> ${intern.duration}
                </div>
                <div class="detail-item">
                    <i class="fas fa-calendar-alt"></i> Apply by: ${intern.deadline}
                </div>
            </div>
            <div class="card-footer">
                <div class="stipend">${intern.stipend || 'Unpaid'}</div>
                <button class="btn btn-outline" onclick="openDetails(${intern.id})">
                    View Details
                </button>
            </div>
        </div>
    `).join('');
}

// Open modal with details
function openDetails(id) {
    // Find internship from state
    const intern = internships.find(i => i.id === id);
    if (!intern) return;

    // Populate modal
    document.getElementById('modalCompany').textContent = intern.company_name;
    document.getElementById('modalRole').textContent = intern.role;
    document.getElementById('modalLocation').textContent = intern.location;
    document.getElementById('modalDuration').textContent = intern.duration;
    document.getElementById('modalStipend').textContent = intern.stipend || 'Unpaid';
    document.getElementById('modalDeadline').textContent = intern.deadline;
    document.getElementById('modalDescription').textContent = intern.description || 'No description provided.';
    document.getElementById('modalRequirements').textContent = intern.requirements || 'No requirements provided.';

    // Show modal
    modal.classList.add('active');
}
