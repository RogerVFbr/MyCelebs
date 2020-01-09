export class Logger {

    constructor(user, opType) {
        this.user = user;
        this.opType = opType;
    }

    getLog() {
        var logs = JSON.parse(localStorage.getItem("logger") || "[]");
        return logs;
    }

    log(message) {
        var today = new Date();
        var day = today.getDate()<10 ? "0" + today.getDate() : today.getDate();
        var month = (today.getMonth()+1)<10 ? "0" + (today.getMonth()+1) : today.getMonth()+1;
        var year = today.getFullYear()<10 ? "0" + today.getFullYear() : today.getFullYear();
        var hour = today.getHours()<10 ? "0" + today.getHours() : today.getHours();
        var minutes = today.getMinutes()<10 ? "0" + today.getMinutes() : today.getMinutes();
        var seconds = today.getSeconds()<10 ? "0" + today.getSeconds() : today.getSeconds();
        var date = day + '/'+ month + '/'+ year + " - " + hour + ":" + minutes + ":" + seconds;
        var log = {
            time: date,
            name: this.user,
            type: this.opType,
            message: message
        }

        var logs = JSON.parse(localStorage.getItem("logger") || "[]");
        logs.unshift(log);
        localStorage.setItem("logger", JSON.stringify(logs));
    }

    clearLog() {
        localStorage.setItem("logger", JSON.stringify([]));
    }
}