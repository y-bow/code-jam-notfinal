// Sample Data fallback (in case admin is opened before main)
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
    }
];

// DOM Elements
const tableBody = document.getElementById('internshipsTableBody');
const formModal = document.getElementById('formModal');
const deleteModal = document.getElementById('deleteModal');
const internshipForm = document.getElementById('internshipForm');

// Buttons
const openAddModalBtn = document.getElementById('openAddModalBtn');
const closeFormModalBtn = document.getElementById('closeFormModalBtn');
const cancelFormBtn = document.getElementById('cancelFormBtn');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

// Form Fields
const formId = document.getElementById('internshipId');
const formCompany = document.getElementById('companyName');
const formRole = document.getElementById('roleTitle');
const formLocation = document.getElementById('location');
const formDuration = document.getElementById('duration');
const formStipend = document.getElementById('stipend');
const formDeadline = document.getElementById('deadline');
const formDescription = document.getElementById('description');
const formRequirements = document.getElementById('requirements');
const modalTitle = document.getElementById('modalTitle');

// State
let internships = [];
let deleteId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Initialize LocalStorage if empty
    if (!localStorage.getItem('internships')) {
        localStorage.setItem('internships', JSON.stringify(sampleInternships));
    }
    
    fetchInternships();

    // Open/Close Modals
    openAddModalBtn.addEventListener('click', () => openFormModal());
    closeFormModalBtn.addEventListener('click', closeFormModal);
    cancelFormBtn.addEventListener('click', closeFormModal);
    
    cancelDeleteBtn.addEventListener('click', closeDeleteModal);
    confirmDeleteBtn.addEventListener('click', deleteInternship);
    
    // Close modals on overlay click
    [formModal, deleteModal].forEach(m => {
        m.addEventListener('click', (e) => {
            if (e.target === m) m.classList.remove('active');
        });
    });

    // Form Submit
    internshipForm.addEventListener('submit', handleFormSubmit);
});

function fetchInternships() {
    try {
        internships = JSON.parse(localStorage.getItem('internships')) || [];
        renderTable();
    } catch (error) {
        console.error('Error fetching data:', error);
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Failed to load data from LocalStorage.</td></tr>`;
    }
}

function renderTable() {
    if (internships.length === 0) {
        tableBody.innerHTML = `<tr><td colspan="5" style="text-align: center;">No internships found.</td></tr>`;
        return;
    }

    tableBody.innerHTML = internships.map(intern => `
        <tr>
            <td style="font-weight: 500; color: var(--text-main);">${intern.company_name}</td>
            <td>${intern.role}</td>
            <td><span class="badge">${intern.location}</span></td>
            <td>${intern.deadline}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-outline" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="openFormModal(${intern.id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-danger" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;" onclick="openDeleteModal(${intern.id})">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Modal Form Management (Add/Edit)
function openFormModal(id = null) {
    if (id) {
        // Edit Mode
        const intern = internships.find(i => i.id === id);
        if (intern) {
            modalTitle.textContent = 'Edit Internship';
            formId.value = intern.id;
            formCompany.value = intern.company_name;
            formRole.value = intern.role;
            formLocation.value = intern.location;
            formDuration.value = intern.duration;
            formStipend.value = intern.stipend || '';
            formDeadline.value = intern.deadline;
            formDescription.value = intern.description;
            formRequirements.value = intern.requirements;
        }
    } else {
        // Add Mode
        modalTitle.textContent = 'Add Internship';
        internshipForm.reset();
        formId.value = '';
    }
    formModal.classList.add('active');
}

function closeFormModal() {
    formModal.classList.remove('active');
    internshipForm.reset();
}

function handleFormSubmit(e) {
    e.preventDefault();
    
    const isEdit = !!formId.value;
    
    const data = {
        company_name: formCompany.value,
        role: formRole.value,
        location: formLocation.value,
        duration: formDuration.value,
        stipend: formStipend.value,
        deadline: formDeadline.value,
        description: formDescription.value,
        requirements: formRequirements.value
    };

    try {
        if (isEdit) {
            // Update existing
            const index = internships.findIndex(i => i.id === parseInt(formId.value));
            if (index !== -1) {
                internships[index] = { ...internships[index], ...data };
            }
        } else {
            // Create new
            const newId = internships.length > 0 ? Math.max(...internships.map(i => i.id)) + 1 : 1;
            internships.push({ id: newId, ...data });
        }
        
        // Save back to LocalStorage
        localStorage.setItem('internships', JSON.stringify(internships));
        
        closeFormModal();
        fetchInternships();
    } catch (error) {
        console.error('Error saving:', error);
        alert('An error occurred while saving.');
    }
}

// Delete Management
function openDeleteModal(id) {
    deleteId = id;
    deleteModal.classList.add('active');
}

function closeDeleteModal() {
    deleteId = null;
    deleteModal.classList.remove('active');
}

function deleteInternship() {
    if (!deleteId) return;

    try {
        internships = internships.filter(i => i.id !== deleteId);
        localStorage.setItem('internships', JSON.stringify(internships));
        
        closeDeleteModal();
        fetchInternships();
    } catch (error) {
        console.error('Error deleting:', error);
        alert('An error occurred while deleting.');
        closeDeleteModal();
    }
}
