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

function loadProfile() {
    $.get({
        url: "/api/account/",
        dataType: "json",
        success: function(data) {
            const username = $("#username");
            username.text(data.username);
            username.removeClass("is-skeleton");

            const balance = $("#balance");
            balance.text("$" + Number(data.balance).toFixed(2));
            balance.removeClass("is-skeleton");
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