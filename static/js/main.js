// This is the main JavaScript file for your portfolio.
// We will add animations and interactive features here.

document.addEventListener('DOMContentLoaded', (event) => {
    console.log('Portfolio site is loaded and ready for animations!');

    // Example: Add a class to a project card on hover
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.classList.add('hovered');
        });
        card.addEventListener('mouseleave', () => {
            card.classList.remove('hovered');
        });
    });
});
