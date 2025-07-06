document.addEventListener('mousemove', function(e) {
    // Create a new particle element
    const particle = document.createElement('div');
    particle.className = 'mouse-particle';
    
    // Randomize particle size slightly for a more organic feel
    const size = Math.random() * 5 + 3; // Size between 3px and 8px
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;

    // Position the particle at the cursor
    particle.style.left = `${e.clientX - size / 2}px`;
    particle.style.top = `${e.clientY - size / 2}px`;

    // Optional: Add some color variation
    const colors = ['#FF00FF', '#00FFFF', '#fdbb2d']; // Magenta, Cyan, Gold
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    particle.style.backgroundColor = randomColor;

    // Add to the body
    document.body.appendChild(particle);

    // Animate its appearance and then removal
    setTimeout(() => {
        particle.style.opacity = '1';
        particle.style.transform = 'scale(1)';
    }, 10); // Small delay to trigger transition

    setTimeout(() => {
        particle.style.opacity = '0';
        particle.style.transform = 'scale(0)';
        // Remove from DOM after transition completes to prevent buildup
        particle.addEventListener('transitionend', () => particle.remove());
    }, 500); // Particle stays for 0.5 seconds
});