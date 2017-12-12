var escapeRegExp;

(function () {
    // Referring to the table here:
    // https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/regexp
    // these characters should be escaped
    // \ ^ $ * + ? . ( ) | { } [ ]
    // These characters only have special meaning inside of brackets
    // they do not need to be escaped, but they MAY be escaped
    // without any adverse effects (to the best of my knowledge and casual testing)
    // : ! , =
    // my test "~!@#$%^&*(){}[]`/=?+\|-_;:'\",<.>".match(/[\#]/g)

    var specials = [
            // order matters for these
            "-"
            , "["
            , "]"
            // order doesn't matter for any of these
            , "/"
            , "{"
            , "}"
            , "("
            , ")"
            , "*"
            , "+"
            , "?"
            , "."
            , "\\"
            , "^"
            , "$"
            , "|"
        ]

    // I choose to escape every character with '\'
    // even though only some strictly require it when inside of []
        , regex = RegExp('[' + specials.join('\\') + ']', 'g')
        ;

    escapeRegExp = function (str) {
        return str.replace(regex, "\\$&");
    };

    // test escapeRegExp("/path/to/res?search=this.that")
}());

function strTruncate_(str, n, useWordBoundary) {
    var singular,
        tooLong = str.length > n;
    useWordBoundary = useWordBoundary || true;

    // Edge case where someone enters a ridiculously long string.
    str = tooLong ? str.substr(0, n-1) : str;

    singular = (str.search(/\s/) === -1) ? true : false;
    if(!singular) {
      str = useWordBoundary && tooLong ? str.substr(0, str.lastIndexOf(' ')) : str;
    }

    return  tooLong ? str + '&hellip;' : str;
}
