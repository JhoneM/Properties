function initialize_rrss() {

    const facebookBtn = document.querySelector(".s_share_facebookBtn");
    const twitterBtn = document.querySelector(".s_share_twitterBtn");
    const whatsappBtn = document.querySelector(".s_share_whatsappBtn");

    let postUrl = document.location.href;
    let propertyTitle = document.getElementById('property-head').innerHTML;

    facebookBtn.setAttribute(
        "href",
        `https://www.facebook.com/sharer/sharer.php?u=${postUrl}`
    );

    twitterBtn.setAttribute(
        "href",
        `https://twitter.com/share?url=${postUrl}&text=${propertyTitle}`
    );

    whatsappBtn.setAttribute(
        "href",
        `https://wa.me/?text=${propertyTitle} ${postUrl}`
    );
}

window.addEventListener("load", initialize_rrss);