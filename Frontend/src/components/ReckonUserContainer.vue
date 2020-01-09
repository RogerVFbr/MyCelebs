<template>

    <div id="deleteusercontainer" class="container" :class="{ invisible: !visible, visible: visible }">

        <div class="row">

            <div class="col s2 m2 l4 xl4"></div>

            <div id="deleteusercontent" class="col s8 m8 l4 xl4 z-depth-3">

                <div class="row titlerow">
                    <div class="col s12 m12 l12">
                        <h3 class="white-text">Delete user</h3>
                    </div>
                </div>

                <div class="row formrow">

                    <p class="white-text confirmation-message"
                       :class="{ invisible: !deleteContent.isCompleted, visible: deleteContent.isCompleted }">
                        Confirm user deletion?
                    </p>

                    <div class="deletecontainer" :class="{ invisible: deleteContent.isCompleted || errorContent.show, visible: !deleteContent.isCompleted && !errorContent.show}">
                        <div class="deletecontainercontent">
                            <div class="white-text loading-text">{{ deleteContent.message }}</div>
                            <div class="preloader-wrapper small active">
                                <div class="spinner-layer spinner-green-only">
                                    <div class="circle-clipper left">
                                        <div class="circle"></div>
                                    </div><div class="gap-patch">
                                    <div class="circle"></div>
                                </div><div class="circle-clipper right">
                                    <div class="circle"></div>
                                </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="errorcontainer" :class="{ invisible: !errorContent.show, visible: errorContent.show }">
                        <div class="errorcontainercontent">
                            <h4 class="white-text">Error</h4>
                            <p class="white-text">{{errorContent.message}}</p>
                        </div>
                    </div>

                </div>

                <div class="row buttonrow">

                    <div class="col s12 m12 l12">

                        <button class="waves-effect waves-light btn-small teal darken-4 registerbutton"
                                type="submit"
                                @click="deleteUser()"
                                :class="{ buttondisabled: !deleteContent.isCompleted }">
                            Confirm
                            <i class="material-icons right">send</i>
                        </button>

                        <button class="waves-effect waves-light btn-small red darken-4 closebutton"
                                type="submit"
                                @click="close()"
                                :class="{ buttondisabled: !deleteContent.isCompleted }">
                            Cancel
                            <i class="material-icons right">cancel</i>
                        </button>

                    </div>

                </div>

            </div>

            <div class="col s2 m2 l4 xl4"></div>

        </div>

    </div>

</template>


<script>
    export default {
        name: "reckon-user-container",
        props: {
            userId: {},
            onComplete: {},
            onClose: {},
            visible: {}
        },
    }
</script>

<style scoped>

    #deleteusercontainer {
        position: absolute;
        left: 50%;
        transform: translate(-50%);
        top: 20px;
    }



    .formrow {
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .titlerow {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px 10px 10px 10px;
    }

    .buttonrow {
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        height: 42px;
    }

    .buttondisabled {
        opacity: 0.2;
        pointer-events: none
    }

    .confirmation-message {
        margin-top: 15px;
    }

    .errorcontainer {
        position: absolute;
        top: 72px;
        bottom: 60px;
        left: 7px;
        right: 7px;
        background-color: rgba(220,20,60, 0.5);
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .errorcontainercontent, .deletecontainercontent {
        text-align: center;
    }

    .deletecontainer {
        position: absolute;
        top: 72px;
        bottom: 60px;
        left: 7px;
        right: 7px;
        background-color: rgba(255,255,255, 0.1);
        border-radius: 0.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .deletecontainercontent {
        text-align: center;
        animation: fadeInOut6 1s ease reverse forwards infinite
    }

    @keyframes fadeInOut6 {
        0% { opacity: 0.4 }
        50% { opacity: 0.8 }
        100% { opacity: 0.4 }
    }

    .loading-text {
        margin-bottom: 10px;
    }

    .closebutton {
        position: absolute;
        top: 10px;
        right: 10px;
    }

    .registerbutton {
        position: absolute;
        top: 10px;
        left: 10px;
        transition: all 0.3s;
    }

    .col {
        flex-basis: auto !important;
    }

    .row {
        margin-bottom:  10px;
    }

    .visible {
        visibility: visible;
        opacity: 1;
        z-index: 10;
        transition: visibility 0s linear 0s, opacity 0.35s linear;
    }

    .invisible {
        visibility: hidden;
        opacity: 0;
        z-index: -10;
        transition: visibility 0s linear 0.35s, opacity 0.35s linear;
    }

</style>