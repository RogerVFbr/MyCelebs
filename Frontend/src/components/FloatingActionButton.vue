<template>
    <div id="fab-button" class="floating-button purple darken-4 waves-effect wavese-light hoverable" @click="triggerOnclick" :class="{ hideclass: !show , showclass: show}">
        <font-awesome-icon icon="plus" class="floating-button-icon white-text"/>
    </div>
</template>

<script>
    export default {
        name: "floating-action-button",
        props: {
            show: {},
            onclick: {},
        },
        methods: {
            triggerOnclick: function() { this.onclick(); }
        }
    }
</script>

<style scoped>

    .floating-button {
        position:fixed;
        width:55px;
        height:55px;
        bottom:20px;
        right:20px;
        border-radius:50px;
        text-align:center;
        box-shadow: 5px 5px 30px rgba(0, 0, 0, .4);
        opacity: 0;
    }

    .floating-button-icon {
        margin-top: 18px;
        font-size: 1.3rem;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            bottom: 10px;
            right: 10px;
            transform: scale(.8);
            -webkit-transform: scale(.8);
        }
        to {
            opacity: 1;
            bottom: 20px;
            right: 20px;
            transform: scale(1);
            -webkit-transform: scale(1);
        }
    }

    @keyframes fadeOut {
        from {
            opacity: 1;
            bottom: 20px;
            right: 20px;
            transform: scale(1);
            -webkit-transform: scale(1);
        }
        to {
            opacity: 0;
            bottom: 10px;
            right: 10px;
            transform: scale(.8);
            -webkit-transform: scale(.8);
        }
    }

    .showclass {
        z-index: 1000;
        animation-name: fadeIn;
        animation-duration: 1.7s;
        animation-fill-mode: forwards;
        opacity: 0;
    }

    .hideclass {
        z-index: -1000;
        animation-name: fadeOut;
        animation-duration: 0.25s;
        animation-fill-mode: forwards;
        opacity: 1;
    }

</style>