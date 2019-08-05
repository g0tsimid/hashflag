$.hashflag_globals = {
    keywords : []
};

function addKeyword() {
    var keyword = $("#new-alert-keyword")[0].value.toLowerCase();
    if (!keyword) {
        return;
    } else if (keyword.length > 40) {
        return;
    } else if ($.inArray(keyword, $.hashflag_globals.keywords) >= 0) {
        $("#new-alert-keyword")[0].value = "";
        return
    }

    $.hashflag_globals.keywords.push(keyword);
    var new_li = $(document.createElement("li"))
        .html(keyword)
        .appendTo(".alert-keyword-list");

    $(document.createElement("a"))
        .html("&times;")
        .attr("href", "#")
        .addClass("alert-remove-keyword")
        .click(function() {
            new_li.fadeOut(300, function() { // Remove li once animation is complete.
                $(this).remove();
            });
            $.hashflag_globals.keywords = $.hashflag_globals.keywords.filter(function(e) {
                return e != keyword;
            });
        }).prependTo(new_li);
    $("#new-alert-keyword")[0].value = "";

    // Scroll to the new keyword at the bottom of the list.
    $(".alert-keyword-list").animate({
        scrollTop: $(".alert-keyword-list")[0].scrollHeight
    });
}

function disableFrequencySettings() {
    $(".alert-frequency-settings input").attr("disabled", "disabled");
}

function enableFrequencySettings() {
    $(".alert-frequency-settings input").removeAttr("disabled");
}

function submit() {
    addKeyword(); // Add any keywords that might be sitting in the input box.
    if (!$("#id_email")[0].value) {
        alert("You must enter an email address.");
        return;
    } else if (!($.hashflag_globals.keywords.length > 0)) {
        alert("You must enter at least one keyword.");
        return;
    }

    if (!$("#size-input")[0].value) {
        $("#size-input")[0].value = "20";
    }

    $("#track-keywords")
        .attr("value", $.hashflag_globals.keywords.join(", "));

    $("#create-alert").submit();
}