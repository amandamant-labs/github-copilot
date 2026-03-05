document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear existing options but keep the default option
      while (activitySelect.options.length > 1) {
        activitySelect.remove(1);
      }

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsHtml = details.participants.map(email => {
          const participantName = email.split('@')[0];
          const initials = participantName.split('.').map(n => n[0].toUpperCase()).join('');
          return `
            <div class="participant" title="${email}">
              <div class="participant-avatar">${initials}</div>
              <span class="participant-name">${participantName}</span>
              <button class="participant-remove" data-activity="${name}" data-email="${email}" title="Remover participante">×</button>
            </div>
          `;
        }).join('');

        const occupancy = Math.round((details.participants.length / details.max_participants) * 100);

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <div class="availability-info">
            <div class="availability-bar">
              <div class="availability-fill" style="width: ${occupancy}%"></div>
            </div>
            <span class="availability-text">${details.participants.length}/${details.max_participants} • ${spotsLeft} vagas restantes</span>
          </div>
          <div class="participants-section">
            <h5>Participantes (${details.participants.length})</h5>
            <div class="participants-list">
              ${participantsHtml || '<p class="no-participants">Nenhum participante ainda</p>'}
            </div>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        // Reload activities to reflect the new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle participant removal
  document.addEventListener("click", async (event) => {
    if (event.target.classList.contains("participant-remove")) {
      const email = event.target.getAttribute("data-email");
      const activityName = event.target.getAttribute("data-activity");

      if (confirm(`Tem certeza que deseja remover ${email}?`)) {
        try {
          const response = await fetch(
            `/activities/${encodeURIComponent(activityName)}/remove?email=${encodeURIComponent(email)}`,
            {
              method: "DELETE",
            }
          );

          if (response.ok) {
            // Reload activities to reflect the change
            fetchActivities();
            messageDiv.textContent = "Participante removido com sucesso!";
            messageDiv.className = "success";
            messageDiv.classList.remove("hidden");

            // Hide message after 3 seconds
            setTimeout(() => {
              messageDiv.classList.add("hidden");
            }, 3000);
          } else {
            const error = await response.json();
            messageDiv.textContent = error.detail || "Erro ao remover participante";
            messageDiv.className = "error";
            messageDiv.classList.remove("hidden");
          }
        } catch (error) {
          messageDiv.textContent = "Erro ao remover participante";
          messageDiv.className = "error";
          messageDiv.classList.remove("hidden");
          console.error("Error removing participant:", error);
        }
      }
    }
  });

  // Initialize app
  fetchActivities();
});
