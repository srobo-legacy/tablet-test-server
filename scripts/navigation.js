(function() {

    var changeSection = function(name) {
        console.log("Changing section to:", name);

        var sections = document.querySelectorAll("section");
        for (var i = 0; i < sections.length; i++) {
            sections[i].hidden = true;
        }

        document.querySelector("section#" + name).hidden = false;
    };

    changeSection("status");

    var links = document.querySelectorAll("a[data-section]");
    for (var i = 0; i < links.length; i++) {
        links[i].onclick = changeSection.bind(undefined, links[i].dataset.section);
    }

}());
