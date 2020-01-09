<template>
    <div id="app">
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <Navbar :key="$route.fullPath"></Navbar>
        <div class="row">
            <div class="col-sm-12 page home">
                <transition name="router-anim">
                    <router-view :key="$route.fullPath"/>
                </transition>
            </div>
        </div>
    </div>
</template>

<style>

    @import "https://cdn.jsdelivr.net/npm/animate.css@3.5.1";

    #app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
        /*height: 100%;*/
        /*overflow-x: hidden;*/
    }

    .page {
        position: fixed;
        width: inherit;
    }

    body {
        background-color: transparent !important;
    }

    .router-anim-enter-active {
        animation: coming .7s;
        animation-delay: .2s;
        opacity: 0;
    }

    .router-anim-leave-active {
        animation: going .2s;
    }

    @keyframes coming {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @keyframes going {
        from { }
        to { opacity: 0; }
    }


</style>

