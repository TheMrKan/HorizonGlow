function tryHandleAuthError(jqXHR) {
    if (jqXHR.status == 401) {
        window.location.href = "/auth/login/"
    }
}

function showError(jqXHR) {
    let text = "An internal error occured during the operation. Please, try again."
    try {
        let errors = JSON.parse(jqXHR.responseText);
        console.error(errors);
        text = Object.values(errors)[0];
    }
    catch (e) {
        console.error("Failed to parse JSON error: " + e);
        console.error("Response: " + jqXHR.responseText);
    }
    notify(text, "error", 3000);
}

$(function() {
    $('body').append("<div class='notifications'></div>");
});

function notify(msg, mode, duration) {
    const classy = "notification";
    $(`#${classy}`).remove();
    $('.notifications').append(`
        <div id='${classy}' class='notification is-${mode} slideInRight'>
            <span class="icon">
                <i class="fa-solid fa-triangle-exclamation"></i>
            </span>
            ${msg}
        </div>
    `);
    const elem = $(`#${classy}`);

    elem.click(function() {
        $(this).removeClass('slideInRight');
        $(this).addClass('slideOutRight');
        setTimeout(function() {
            $(this).remove();
        }, 350);
    });

    setTimeout(function() {
        elem.removeClass('slideInRight');
        elem.addClass('slideOutRight');
        setTimeout(function() {
            elem.remove();
        }, 350);
    }, duration);
}

let profileBalance = 0;
const onProfileLoaded = new Event("profileLoaded");
function loadProfile() {
    $.get({
        url: "/api/account/",
        dataType: "json",
        success: function(data) {
            const username = $("#username");
            username.text(data.username);
            username.removeClass("is-skeleton");

            profileBalance = data["balance"];
            const balance = $("#balance");
            balance.text("$" + Number(profileBalance).toFixed(2));
            balance.removeClass("is-skeleton");

            const isSeller = data["isSeller"];
            if (isSeller) {
                const dropdown = $("#header-user-dropdown-menu .dropdown-content");
                if (dropdown.length) {
                    const divider = $("<hr class=\"dropdown-divider\" />");
                    dropdown.find(".dropdown-divider").first().before(divider)
                    divider.after(
                        $('<a id="menu-dropdown-seller" href="/seller" class="dropdown-item"><span class="icon"><i class="fas fa-store" aria-hidden="true"></i></span> Seller </a>')
                    );
                }
            }

            document.dispatchEvent(onProfileLoaded);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            tryHandleAuthError(jqXHR);

            showError(jqXHR);
        }
    });
}

function logout() {
    $.post({
        url: "/api/auth/logout/",
        success: function(data) {
            window.location.href = "/auth/login/";
        },
        error: function(jqXHR, textStatus, errorThrown) {
            showError(jqXHR);
        }
    });
}

function setFieldError(field, text=null, originalText=null) {
    const active = text !== "" && text !== null;
    field.find("input").toggleClass("is-danger", active);
    field.find(".is-right").toggle(active);
    field.find(".help").text(text);

    const color = active ? "var(--bulma-danger)" : "inherit";
    field.find("span .file-label").css("color", color).text(active ? text : originalText);

}

function toDateUS(date) {
    return ('0' + (date.getMonth() + 1)).slice(-2) + '/' + ('0' + date.getDate()).slice(-2);
}

function toDateUSFull(date) {
    return toDateUS(date) + "/" + date.getFullYear();
}
