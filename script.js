document.addEventListener('DOMContentLoaded', () => {
    const heroSection = document.querySelector('.hero-section');
    const ctaButton = document.getElementById('cta-button');
    const quizSection = document.getElementById('quiz-section');
    const resultsSection = document.getElementById('results-section');
    const quizQuestions = document.querySelectorAll('.question-box');
    const resultsContent = document.getElementById('results-content');
    const otherResourcesSection = document.getElementById('other-resources');
    const otherResourcesList = document.getElementById('other-resources-list');
    
    let currentQuestionIndex = 0;
    const userAnswers = {};

    // Master list of all resources with their category tags and costs
    const allResources = [
        { name: "Duolingo", url: "https://www.duolingo.com", tags: ["travel", "hobby", "low", "visual", "kinesthetic"], cost: "Free / $7/mo" },
        { name: "Babbel", url: "https://www.babbel.com", tags: ["career", "medium", "visual", "auditory"], cost: "$10-15/mo" },
        { name: "Rosetta Stone", url: "https://www.rosettastone.com", tags: ["career", "high", "visual", "auditory"], cost: "$12/mo" },
        { name: "Memrise", url: "https://www.memrise.com", tags: ["travel", "low", "visual", "kinesthetic"], cost: "Free / $8.50/mo" },
        { name: "Pimsleur", url: "https://www.pimsleur.com", tags: ["auditory", "medium", "high", "travel", "career"], cost: "$15-20/mo" },
        { name: "FluentU", url: "https://www.fluentu.com", tags: ["hobby", "high", "visual", "auditory"], cost: "$20-30/mo" },
        { name: "iTalki", url: "https://www.italki.com", tags: ["career", "high", "kinesthetic", "medium"], cost: "$5-20/lesson" },
        { name: "Busuu", url: "https://www.busuu.com", tags: ["travel", "hobby", "low", "visual", "kinesthetic"], cost: "Free / $6-10/mo" },
        { name: "Anki", url: "https://apps.ankiweb.net/", tags: ["hobby", "low", "kinesthetic"], cost: "Free / One-time cost" },
        { name: "HelloTalk", url: "https://www.hellotalk.com", tags: ["travel", "hobby", "low", "kinesthetic"], cost: "Free / $7/mo" },
        { name: "Coffee Break Languages Podcast", url: "https://coffeebreaklanguages.com", tags: ["auditory", "low", "medium", "travel", "hobby"], cost: "Free" }
    ];

    // Initial CTA button to start the quiz
    ctaButton.addEventListener('click', () => {
        heroSection.classList.add('hidden');
        quizSection.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Handle button selections with event delegation
    quizSection.addEventListener('click', (e) => {
        // Check if the clicked element is a quiz option button
        if (e.target.tagName === 'BUTTON' && e.target.closest('.options')) {
            const selectedButton = e.target;
            const parentOptions = selectedButton.closest('.options');

            // Remove the 'selected' class from all other buttons in the same question
            parentOptions.querySelectorAll('button').forEach(btn => btn.classList.remove('selected'));
            
            // Add the 'selected' class to the clicked button
            selectedButton.classList.add('selected');

            // Store the user's answer
            const questionId = `q${currentQuestionIndex + 1}`;
            userAnswers[questionId] = selectedButton.dataset.value;
    
            // Hide the current question
            quizQuestions[currentQuestionIndex].classList.add('hidden');
            
            // Advance to the next question
            currentQuestionIndex++;
    
            // Check if there are more questions or if the quiz is finished
            if (currentQuestionIndex < quizQuestions.length) {
                // Show the next question
                quizQuestions[currentQuestionIndex].classList.remove('hidden');
            } else {
                // All questions answered, show results
                generateResults();
                quizSection.classList.add('hidden');
                resultsSection.classList.remove('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    });
    
    // Function to generate and display the results
    function generateResults() {
        resultsContent.innerHTML = '';
        otherResourcesList.innerHTML = '';

        const userTags = Object.values(userAnswers);
        
        // Calculate scores for each resource
        const scoredResources = allResources.map(resource => {
            let score = 0;
            userTags.forEach(userTag => {
                if (resource.tags.includes(userTag)) {
                    score++;
                }
            });
            const percentage = (score / userTags.length) * 100;
            return {
                ...resource,
                score,
                percentage: Math.round(percentage)
            };
        });

        // Sort by score (descending)
        scoredResources.sort((a, b) => b.score - a.score);

        const topThree = scoredResources.slice(0, 3);
        const otherOptions = scoredResources.slice(3);

        // Display top three recommendations
        const topList = document.createElement('ul');
        topList.classList.add('resource-list');
        topList.classList.add('result-item');
        topThree.forEach(rec => {
            const listItem = document.createElement('li');
            listItem.innerHTML = `
                <div>
                    <a href="${rec.url}" target="_blank">${rec.name}</a>
                    <span class="cost-badge">${rec.cost}</span>
                </div>
                <span class="match-percentage">${rec.percentage}% Match</span>
            `;
            topList.appendChild(listItem);
        });
        
        const topRecommendationsTitle = document.createElement('h3');
        topRecommendationsTitle.textContent = "Your Top 3 Recommendations";
        resultsContent.appendChild(topRecommendationsTitle);
        resultsContent.appendChild(topList);

        // Display other resources
        if (otherOptions.length > 0) {
            otherResourcesSection.classList.remove('hidden');
            otherOptions.forEach(rec => {
                const listItem = document.createElement('li');
                listItem.innerHTML = `
                    <div>
                        <a href="${rec.url}" target="_blank">${rec.name}</a>
                        <span class="cost-badge">${rec.cost}</span>
                    </div>
                    <span class="match-percentage">${rec.percentage}% Match</span>
                `;
                otherResourcesList.appendChild(listItem);
            });
        }
    }
});
