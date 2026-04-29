const BASE_URL = "https://roblox-github-profile-badge.vercel.app";
//const BASE_URL = "http://localhost:8000";

form = document.getElementById("badge-form");
user = document.getElementById("user");
generateBtn = document.getElementById("generate-preview");
previewCnt = document.getElementById("preview-container");
output = document.getElementById("github-output");
copybtn = document.getElementById("copy-btn")

centeredCB = document.getElementById("centered");
redirectCB = document.getElementById("redirect");

var centered = centeredCB.checked;
var redirect = redirectCB.checked;

centeredCB.addEventListener("change", function () {
    centered = centeredCB.checked;
});

redirectCB.addEventListener("change", function () {
    redirect = redirectCB.checked;
});

generateBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const badge_url = generate_badge_url(user.value);
    const redirect_url = generate_redirect_url(user.value);

    previewCnt.innerHTML = "Loading...";

    const newImg = document.createElement("img");

    newImg.onload = function () {
        previewCnt.innerHTML = "";

        let finalElement;

        if (redirect) {
            const newAnchor = document.createElement("a");
            newAnchor.href = redirect_url;
            newAnchor.target = "_blank";
            newAnchor.append(newImg);
            finalElement = newAnchor;
        } else {
            finalElement = newImg;
        }

        if (centered) {
            const wrapper = document.createElement("div");
            wrapper.setAttribute("align", "center");
            wrapper.append(finalElement);
            previewCnt.style.justifyContent = "center";
            previewCnt.append(wrapper);
        } else {
            previewCnt.style.justifyContent = "flex-start";
            previewCnt.append(finalElement);
        }

        output.value = previewCnt.innerHTML;
    };

    newImg.onerror = function () {
        previewCnt.innerHTML = "Error: Could not load badge.";
    };

    newImg.src = badge_url;
});

copybtn.addEventListener("click", function () {
    output.select();
    output.setSelectionRange(0, 99999);

    navigator.clipboard.writeText(output.value);

    alert("Copied the text: " + output.value);
});


function generate_badge_url(id_or_name) {
    return BASE_URL + "/user/" + id_or_name
}

function generate_redirect_url(id_or_name) {
    return BASE_URL + "/redirect/" + id_or_name
}

function fetch_image(badge_url) {
    return fetch(badge_url).then(function (response) {
        if (!response.ok) throw new Error('Image not found');
        return response.blob();
    });
}