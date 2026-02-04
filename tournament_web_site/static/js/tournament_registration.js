(function() {
    'use strict';

    const teamsDataEl = document.getElementById('teams-data');
    if (!teamsDataEl) return;

    const config = JSON.parse(teamsDataEl.textContent);
    const maxRosterSize = parseInt(config.max_roster_size, 10);
    const teams = config.teams || {};
    const commanders = config.commanders || {};

    const teamSelect = document.getElementById('team-select');
    const rosterSection = document.getElementById('roster-section');
    const rosterList = document.getElementById('roster-players-list');
    const rosterCountEl = document.getElementById('roster-count');

    let selectedRoster = [];

    function updateCount() {
        if (rosterCountEl) rosterCountEl.textContent = selectedRoster.length;
    }

    function togglePlayer(playerId, isCommander, itemEl) {
        if (isCommander) return;

        const isSelected = selectedRoster.includes(playerId);

        if (isSelected) {
            selectedRoster = selectedRoster.filter(id => id !== playerId);
            itemEl.classList.remove('selected');
        } else if (selectedRoster.length < maxRosterSize) {
            selectedRoster.push(playerId);
            itemEl.classList.add('selected');
        }
        updateCount();
    }

    function createPlayerItem(player, commanderId) {
        const isCommander = player.id === commanderId;
        const isSelected = selectedRoster.includes(player.id);

        const item = document.createElement('div');
        item.className = ['roster-player-item', isSelected && 'selected', isCommander && 'commander'].filter(Boolean).join(' ');
        item.dataset.playerId = player.id;
        item.textContent = isCommander ? player.username + ' (командир)' : player.username;

        item.addEventListener('click', () => togglePlayer(player.id, isCommander, item));

        return item;
    }

    function renderRoster(teamId) {
        const players = teams[teamId] || [];
        const commanderId = commanders[teamId];

        selectedRoster = commanderId ? [commanderId] : [];
        updateCount();

        rosterList.innerHTML = '';
        players.forEach(player => rosterList.appendChild(createPlayerItem(player, commanderId)));
    }

    function onTeamChange() {
        const teamId = teamSelect.value;

        if (teamId) {
            rosterSection.hidden = false;
            renderRoster(teamId);
        } else {
            rosterSection.hidden = true;
            rosterList.innerHTML = '';
            selectedRoster = [];
            updateCount();
        }
    }

    if (teamSelect) {
        teamSelect.addEventListener('change', onTeamChange);
    }

    updateCount();

    // Fetch-запрос для регистрации на турнир
    function getCookie(name) {
        let value = null;
        if (document.cookie && document.cookie !== '') {
            const parts = document.cookie.split(';');
            for (let i = 0; i < parts.length; i++) {
                const part = parts[i].trim();
                if (part.startsWith(name + '=')) {
                    value = decodeURIComponent(part.slice(name.length + 1));
                    break;
                }
            }
        }
        return value;
    }

    const registerForm = document.querySelector('.registration-form');
    const registerBtn = registerForm && registerForm.querySelector('.green-button');

    if (registerBtn && registerForm) {
        registerBtn.addEventListener('click', function() {
            const teamId = teamSelect.value;
            const registerUrl = registerForm.dataset.registerUrl;

            if (!teamId) {
                alert('Выберите команду');
                return;
            }

            const requiredSize = maxRosterSize;
            if (selectedRoster.length !== requiredSize) {
                alert('Выберите ровно ' + requiredSize + ' участников в составе');
                return;
            }

            registerBtn.disabled = true;

            fetch(registerUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    team_id: parseInt(teamId, 10),
                    roster: selectedRoster,
                }),
            })
                .then(function(response) {
                    return response.json().then(function(data) {
                        return { ok: response.ok, data: data };
                    }).catch(function() {
                        return { ok: response.ok, data: {} };
                    });
                })
                .then(function(result) {
                    if (result.ok) {
                        alert('Заявка отправлена!');
                        if (result.data.redirect_url) {
                            window.location.href = result.data.redirect_url;
                        }
                    } else {
                        alert(result.data.error || result.data.message || 'Ошибка при регистрации');
                    }
                })
                .catch(function(err) {
                    alert('Ошибка сети. Попробуйте позже.');
                    console.error(err);
                })
                .finally(function() {
                    registerBtn.disabled = false;
                });
        });
    }
})();
