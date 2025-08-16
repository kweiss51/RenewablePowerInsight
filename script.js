document.addEventListener('DOMContentLoaded', () => {
    const heroSection = document.querySelector('.hero-section');
    const ctaButton = document.getElementById('cta-button');
    const quizSection = document.getElementById('quiz-section');
    const resultsSection = document.getElementById('results-section');
    const nextBtn = document.getElementById('next-btn');
    const quizQuestions = document.querySelectorAll('.question-box');
    const resultsContent = document.getElementById('results-content');
    
    let currentQuestionIndex = 0;
    const userAnswers = {};

    // Recommendations data based on quiz answers
    const recommendations = {
        // Goal-based recommendations
        travel: {
            title: "Your Goal: Travel & Social Connections",
            description: "You're learning a language to connect with people and explore new places. Your plan should focus on conversational skills and practical phrases for real-world situations. Think of it as your verbal passport.",
            resources: [
                { name: "Duolingo: Bite-sized lessons for quick wins", url: "https://www.duolingo.com" }, // Replace with affiliate link
                { name: "Memrise: Learn useful words and phrases through spaced repetition", url: "https://www.memrise.com" }, // Replace with affiliate link
                { name: "HelloTalk: Practice with native speakers for free", url: "https://www.hellotalk.com" } // Replace with affiliate link
            ]
        },
        career: {
            title: "Your Goal: Career & Business Success",
            description: "You're investing in a new skill for professional growth. Your plan will focus on formal language, business vocabulary, and professional communication to help you stand out.",
            resources: [
                { name: "Rosetta Stone: Immersive learning for a strong foundation", url: "https://www.rosettastone.com" }, // Replace with affiliate link
                { name: "Babbel: Focused on conversational confidence for professional settings", url: "https://www.babbel.com" }, // Replace with affiliate link
                { name: "iTalki: Find a professional tutor for 1-on-1 coaching", url: "https://www.italki.com" } // Replace with affiliate link
            ]
        },
        hobby: {
            title: "Your Goal: Personal Growth & Hobby",
            description: "Language learning is a personal journey for you. Your plan will be flexible and fun, allowing you to explore the language at your own pace.",
            resources: [
                { name: "FluentU: Learn with real-world videos (music, movies, news)", url: "https://www.fluentu.com" }, // Replace with affiliate link
                { name: "Busuu: A social network for language learning", url: "https://www.busuu.com" }, // Replace with affiliate link
                { name: "YouTube Language Channels: Free, engaging content from creators", url: "https://www.youtube.com/c/yourfavoritelanguagechannel" } // Replace with affiliate link
            ]
        },
        // Time commitment recommendations
        low: {
            title: "Your Time Commitment: The Busy Learner",
            description: "You have limited time, so we'll focus on consistency. 15 minutes a day is more powerful than 3 hours once a week. Your plan is built for daily micro-progress.",
            resources: [
                { name: "Duolingo: Ideal for quick, daily practice", url: "https://www.duolingo.com" }, // Replace with affiliate link
                { name: "Pimsleur: Audio lessons perfect for commutes", url: "https://www.pimsleur.com" }, // Replace with affiliate link
                { name: "Anki: A flashcard app to memorize key vocabulary efficiently", url: "https://apps.ankiweb.net/" } // Replace with affiliate link
            ]
        },
        medium: {
            title: "Your Time Commitment: The Consistent Learner",
            description: "You've got a solid amount of time to commit. Your plan will balance structured lessons with fun, immersive activities to keep you engaged and progressing.",
            resources: [
                { name: "Babbel: Structured courses to build a strong base", url: "https://www.babbel.com" }, // Replace with affiliate link
                { name: "Netflix with dubbing/subtitles: Immersion with your favorite shows", url: "https://www.netflix.com" },
                { name: "iTalki: Find a tutor to practice speaking once or twice a week", url: "https://www.italki.com" } // Replace with affiliate link
            ]
        },
        high: {
            title: "Your Time Commitment: The Dedicated Learner",
            description: "You're ready to dive deep! Your plan combines comprehensive learning programs with real-life practice to get you to your goals faster.",
            resources: [
                { name: "Rosetta Stone: Comprehensive, immersive lessons", url: "https://www.rosettastone.com" }, // Replace with affiliate link
                { name: "Pimsleur: All-audio lessons for fluency", url: "https://www.pimsleur.com" }, // Replace with affiliate link
                { name: "italki: Schedule multiple conversation sessions weekly", url: "https://www.italki.com" } // Replace with affiliate link
            ]
        },
        // Learning style recommendations
        visual: {
            title: "Your Style: Visual Learner",
            description: "Your brain learns best by seeing. Your plan will be filled with videos, written text, apps with graphics, and flashcards to help you visualize concepts.",
            resources: [
                { name: "FluentU: Learn with authentic videos and interactive subtitles", url: "https://www.fluentu.com" }, // Replace with affiliate link
                { name: "Duolingo: Gamified lessons with visual progress bars", url: "https://www.duolingo.com" }, // Replace with affiliate link
                { name: "Pinterest: Create mood boards with images and vocabulary", url: "https://www.pinterest.com" }
            ]
        },
        auditory: {
            title: "Your Style: Auditory Learner",
            description: "You're a listener. Your plan will emphasize podcasts, audiobooks, music, and spoken conversation to help you internalize the sounds and rhythm of the language.",
            resources: [
                { name: "Pimsleur: All-audio program focused on pronunciation", url: "https://www.pimsleur.com" }, // Replace with affiliate link
                { name: "Coffee Break Languages: Fun and accessible podcast series", url: "https://coffeebreaklanguages.com" },
                { name: "Spotify: Create a playlist of music in your target language", url: "https://www.spotify.com" }
            ]
        },
        kinesthetic: {
            title: "Your Style: Hands-On Learner",
            description: "You learn by doing. Your plan will get you speaking, writing, and interacting with the language right away. You need to be active to make progress.",
            resources: [
                { name: "iTalki: Practice with native speakers and tutors", url: "https://www.italki.com" }, // Replace with affiliate link
                { name: "Anki: Create your own flashcards and use them actively", url: "https://apps.ankiweb.net/" }, // Replace with affiliate link
                { name: "HelloTalk: A language exchange app for real-time practice", url: "https://www.hellotalk.com" } // Replace with affiliate link
            ]
        }
    };

    // Initial CTA button to start the quiz
    ctaButton.addEventListener('click', () => {
        heroSection.classList.add('hidden');
        quizSection.classList.remove('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Handle button selection within each question
    document.querySelectorAll('.options button').forEach(button => {
        button.addEventListener('click', (e) => {
            const parentOptions = e.target.closest('.options');
            parentOptions.querySelectorAll('button').forEach(btn => btn.classList.remove('selected'));
            e.target.classList.add('selected');
        });
    });

    // Handle next button click to progress through the quiz
    nextBtn.addEventListener('click', () => {
        const selectedButton = quizQuestions[currentQuestionIndex].querySelector('.options .selected');
        if (!selectedButton) {
            alert('Please make a selection to continue.');
            return;
        }

        const questionId = `q${currentQuestionIndex + 1}`;
        userAnswers[questionId] = selectedButton.dataset.value;

        quizQuestions[currentQuestionIndex].classList.add('hidden');
        currentQuestionIndex++;

        if (currentQuestionIndex < quizQuestions.length) {
            quizQuestions[currentQuestionIndex].classList.remove('hidden');
        } else {
            generateResults();
            quizSection.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    // Function to generate and display the results
    function generateResults() {
        resultsContent.innerHTML = '';
        const answerKeys = [userAnswers.q1, userAnswers.q2, userAnswers.q3];
        
        // Loop through the answers and build the results section
        answerKeys.forEach(key => {
            if (recommendations[key]) {
                const rec = recommendations[key];
                const section = document.createElement('div');
                section.classList.add('result-item');
                section.innerHTML = `
                    <h3>${rec.title}</h3>
                    <p>${rec.description}</p>
                    <h4>Recommended Resources:</h4>
                    <ul class="resource-list">
                        ${rec.resources.map(res => `<li><a href="${res.url}" target="_blank">${res.name}</a></li>`).join('')}
                    </ul>
                `;
                resultsContent.appendChild(section);
            }
        });
    }
});
