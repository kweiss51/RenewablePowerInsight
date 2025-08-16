document.addEventListener('DOMContentLoaded', () => {
    const heroSection = document.querySelector('.hero-section');
    const ctaButton = document.getElementById('cta-button');
    const quizSelectionSection = document.getElementById('quiz-selection');
    const allQuizSections = document.querySelectorAll('.quiz-section');
    const resultsSection = document.getElementById('results-section');
    const quizCardContainer = document.querySelector('.quiz-card-container');
    const resultsContent = document.getElementById('results-content');
    const otherResourcesSection = document.getElementById('other-resources');
    const otherResourcesList = document.getElementById('other-resources-list');
    const quizSidebar = document.querySelector('.quiz-sidebar');
    
    let currentQuizId = '';
    const userAnswers = {};

    // Master list of all resources with their category tags and costs
    const allResources = [
        { name: "Duolingo", url: "https://www.duolingo.com", tags: ["travel", "hobby", "low", "visual", "kinesthetic", "vocabulary", "games", "micro", "spontaneous", "relaxing"], cost: "Free / $7/mo" },
        { name: "Babbel", url: "https://www.babbel.com", tags: ["career", "medium", "visual", "auditory", "grammar", "structured", "interactive", "textbooks", "speaking"], cost: "$10-15/mo" },
        { name: "Rosetta Stone", url: "https://www.rosettastone.com", tags: ["career", "high", "visual", "auditory", "grammar", "structured", "interactive", "immersion", "speaking"], cost: "$12/mo" },
        { name: "Memrise", url: "https://www.memrise.com", tags: ["travel", "low", "visual", "kinesthetic", "vocabulary", "games", "micro", "relaxing"], cost: "Free / $8.50/mo" },
        { name: "Pimsleur", url: "https://www.pimsleur.com", tags: ["auditory", "medium", "high", "travel", "career", "pronunciation", "structured", "speed", "listening"], cost: "$15-20/mo" },
        { name: "FluentU", url: "https://www.fluentu.com", tags: ["hobby", "high", "visual", "auditory", "vocabulary", "listening", "reading", "media"], cost: "$20-30/mo" },
        { name: "iTalki", url: "https://www.italki.com", tags: ["career", "high", "kinesthetic", "medium", "speaking", "partner", "teacher", "social"], cost: "$5-20/lesson" },
        { name: "Busuu", url: "https://www.busuu.com", tags: ["travel", "hobby", "low", "visual", "kinesthetic", "grammar", "mistake", "community", "social"], cost: "Free / $6-10/mo" },
        { name: "Anki", url: "https://apps.ankiweb.net/", tags: ["hobby", "low", "kinesthetic", "vocabulary", "games", "spontaneous"], cost: "Free / One-time cost" },
        { name: "HelloTalk", url: "https://www.hellotalk.com", tags: ["travel", "hobby", "low", "kinesthetic", "speaking", "partner", "social"], cost: "Free / $7/mo" },
        { name: "Coffee Break Languages Podcast", url: "https://coffeebreaklanguages.com", tags: ["auditory", "low", "medium", "travel", "hobby", "listening", "relaxing"], cost: "Free" }
    ];

    // Initial CTA button to show the quiz selection page
    ctaButton.addEventListener('click', () => {
        heroSection.classList.add('hidden');
        quizSelectionSection.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Handle quiz card selection
    quizCardContainer.addEventListener('click', (e) => {
        const card = e.target.closest('.quiz-card');
        if (card) {
            currentQuizId = card.dataset.quiz;
            quizSelectionSection.classList.add('hidden');
            
            // Show the selected quiz section and its first question
            const targetQuizSection = document.getElementById(`quiz-${currentQuizId}`);
            if (targetQuizSection) {
                targetQuizSection.classList.remove('hidden');
                const firstQuestion = targetQuizSection.querySelector('.question-box');
                if (firstQuestion) {
                    firstQuestion.classList.remove('hidden');
                }
            }
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    // Handle button selections with event delegation
    document.addEventListener('click', (e) => {
        if (e.target.tagName === 'BUTTON' && e.target.closest('.options')) {
            const selectedButton = e.target;
            const parentOptions = selectedButton.closest('.options');

            // Remove selected class from all buttons in the current question
            parentOptions.querySelectorAll('button').forEach(btn => btn.classList.remove('selected'));
            selectedButton.classList.add('selected');

            const questionId = parentOptions.closest('.question-box').dataset.q;
            userAnswers[questionId] = selectedButton.dataset.value;

            // Find the current question and the next one
            const currentQuestion = parentOptions.closest('.question-box');
            
            // Advance to the next question
            const nextQuestion = currentQuestion.nextElementSibling;

            currentQuestion.classList.add('hidden');
            
            if (nextQuestion && nextQuestion.classList.contains('question-box')) {
                nextQuestion.classList.remove('hidden');
            } else {
                // All questions answered, show results
                generateResults();
                allQuizSections.forEach(section => section.classList.add('hidden'));
                resultsSection.classList.remove('hidden');
                window.scrollTo({ top: 0, behavior: 'smooth' });
            }
        }
    });

    // Handle sidebar button clicks
    quizSidebar.addEventListener('click', (e) => {
        if (e.target.classList.contains('sidebar-btn')) {
            const quizToStart = e.target.dataset.quizStart;
            resetQuizState(quizToStart);
        }
    });

    function resetQuizState(quizId) {
        currentQuizId = quizId;
        Object.keys(userAnswers).forEach(key => delete userAnswers[key]);

        allQuizSections.forEach(section => section.classList.add('hidden'));
        resultsSection.classList.add('hidden');
        document.getElementById(`quiz-${currentQuizId}`).classList.remove('hidden');

        const quizQuestions = document.querySelectorAll(`#quiz-${currentQuizId} .question-box`);
        quizQuestions.forEach((q, index) => {
            q.classList.add('hidden');
            if (index === 0) {
                q.classList.remove('hidden');
            }
            q.querySelectorAll('button').forEach(btn => btn.classList.remove('selected'));
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    
    // Function to generate and display the results
    function generateResults() {
        resultsContent.innerHTML = '';
        otherResourcesList.innerHTML = '';

        const userTags = Object.values(userAnswers);
        
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

        scoredResources.sort((a, b) => b.score - a.score);

        const topThree = scoredResources.slice(0, 3);
        const otherOptions = scoredResources.slice(3);

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
