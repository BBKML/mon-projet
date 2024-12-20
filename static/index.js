
document.addEventListener("DOMContentLoaded", function() {
    const actions = document.querySelectorAll('.recent-actions .action-item');
    
    // Ajoutez une animation ou un effet de survol
    actions.forEach(action => {
        action.addEventListener("mouseenter", function() {
            action.style.transform = "scale(1.05)";
            action.style.transition = "transform 0.3s ease";
        });
        
        action.addEventListener("mouseleave", function() {
            action.style.transform = "scale(1)";
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    fetch('/api/rapport/')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('report-table-body');
            data.forEach(document => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${document.title}</td>
                    <td>${document.uploaded_by}</td>
                    <td>${document.uploaded_at}</td>
                    <td>${document.document_type}</td>
                    <td>${document.service}</td>
                    <td>${document.category}</td>
                    <td>${document.archived}</td>
                `;
                tableBody.appendChild(row);
            });
        });
});
