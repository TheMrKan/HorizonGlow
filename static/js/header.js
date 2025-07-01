HEADER_USER_DROPDOWN_ACTIVE = null;

$(function () {
    $('.column.is-12').first().prepend(header);

    if (HEADER_USER_DROPDOWN_ACTIVE !== null) {
        $(`#header-user-dropdown-menu ${HEADER_USER_DROPDOWN_ACTIVE}`).addClass("is-active");
    }
});

const header = `
<div class="box py-1">
    <div class="level">
        <div class="level-left">
            <div class="level-item is-mobile">
                <button onclick="location.href='/'" class="button is-text is-size-5 has-text-weight-semi-bold has-text-primary is-rounded" style="text-decoration: none; --bulma-button-padding-horizontal: 0.5em;">
                    <span class="icon is-small">
                        <i class="fas fa-house"></i>
                    </span>
                    <span>Home</span>
                </button>
                <div id="menu-dropdown" class="dropdown is-hoverable">
                    <div class="dropdown-trigger">
                        <button class="button is-rounded is-text is-size-5"
                                style="text-decoration: none;" aria-haspopup="true"
                                aria-controls="dropdown-menu">
                            <span class="icon mt-1">
                                <i class="fas fa-bars" aria-hidden="true"></i>
                            </span>
                            <span class="icon mt-1">
                                <i class="fas fa-arrow-down" aria-hidden="true"></i>
                            </span>
                            <span>Info</span>
                        </button>
                    </div>
                    <div class="dropdown-menu" role="menu">
                        <div class="dropdown-content pl-2">
                            <a href="/rules" class="dropdown-item is-size-6"><span class="icon"><i class="fas fa-book mr-2" aria-hidden="true"></i></span> Rules </a>
                            <a href="/news" class="dropdown-item is-size-6"><span class="icon"><i class="fas fa-newspaper mr-2" aria-hidden="true"></i></span> News </a>
                             <a href="/feedback" class="dropdown-item is-size-6"><span class="icon"><i class="fas fa-comment mr-2" aria-hidden="true"></i></span> Feedback </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="level-item header-centered">
            <span class="title is-4">MIAMI CASH</span>
        </div>
        <div class="level-right">
            <div class="level-item">
                <span class="has-text-weight-bold mr-1 is-skeleton" id="balance">$38,70</span>
                <span class="icon mr-2">
                    <i class="fas fa-wallet" aria-hidden="true"></i>
                </span>
                <div class="dropdown is-hoverable is-right profile-dropdown">
                    <div class="dropdown-trigger">
                        <button class="button is-rounded is-text" aria-haspopup="true" aria-controls="header-user-dropdown-menu">
                            <span class="is-skeleton" id="username">username</span>
                            <span class="icon">
                                <i class="fas fa-user" aria-hidden="true"></i>
                            </span>
                            <span class="icon">
                                <i class="fas fa-arrow-down" aria-hidden="true"></i>
                            </span>
                        </span>
                        </button>
                    </div>
                    <div class="dropdown-menu" id="header-user-dropdown-menu" role="menu">
                        <div class="dropdown-content pl-2">
                            <a href="/purchases" class="dropdown-item purchases-button"><span class="icon"><i class="fas fa-basket-shopping mr-2" aria-hidden="true"></i></span> My purchases </a>
                            <a href="/profile" class="dropdown-item edit-button"><span class="icon"><i class="fas fa-user-pen mr-2" aria-hidden="true"></i></span> Edit profile </a>
                            <a href="/topup" class="dropdown-item topup-button"><span class="icon"><i class="fa-brands fa-bitcoin mr-2" aria-hidden="true"></i></span> Topup balance </a>
                            <a href="/support" class="dropdown-item support-button"><span class="icon"><i class="fas fa-comments mr-2" aria-hidden="true"></i></span> Support </a>
                            <hr class="dropdown-divider" />
                            <a href="#" onclick="logout()" class="dropdown-item"><span class="icon"><i class="fas fa-right-from-bracket" aria-hidden="true"></i></span> Logout </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
`