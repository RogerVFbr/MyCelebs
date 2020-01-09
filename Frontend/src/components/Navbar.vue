<template>

    <nav>
        <div class="nav-wrapper purple darken-4">
            <div class="container">
                <a href="#" class="brand-logo left"><i class="large material-icons">assignment_ind</i>FaceAuth</a>
                <a href="#" data-target="mobile-demo" class="sidenav-trigger right"><i class="material-icons">menu</i></a>
                <ul id="nav-mobile" class="right hide-on-med-and-down">
                    <li><router-link to="/users" class="routerlinks">Users</router-link></li>
                    <li><router-link to="/reckon" class="routerlinks">Reckon</router-link></li>
                    <!-- Dropdown Trigger -->
                    <li><a class="dropdown-trigger" href="#!" data-target="dropdown1">Logs<i class="material-icons right">arrow_drop_down</i></a></li>
                    <!-- Dropdown Structure -->
                    <ul id="dropdown1" class="dropdown-content">
                        <li><router-link to="/register-log" class="routerlinks">Registrations</router-link></li>
                        <li><router-link to="/reckon-log-success" class="routerlinks">Successful reckons</router-link></li>
                        <li><router-link to="/reckon-log-fail" class="routerlinks">Failed reckons</router-link></li>
                    </ul>

                    <!--<span v-if="isLogged" class="username">{{userEmail}}</span>-->
<!--                    <button v-if="!isLogged" class="waves-effect waves-light btn-small blue darken-2" type="submit" @click="$router.push('login')">Login</button>-->
                    <button v-if="isLogged" class="waves-effect wavese-light btn-small blue darken-2" type="submit" @click="logout">Logout</button>
                </ul>
            </div>
        </div>
        <ul class="sidenav purple darken-4" id="mobile-demo">
            <li><a class="routerlinks" @click="sideNavbarNavigate('users')">Users</a></li>
            <li><a class="routerlinks" @click="sideNavbarNavigate('reckon')">Reckon</a></li>
            <li><div class="divider"></div></li>
            <li><a class="subheader">Logs</a></li>
            <li><a class="routerlinks" @click="sideNavbarNavigate('register-log')">Registrations</a></li>
            <li><a class="routerlinks" @click="sideNavbarNavigate('reckon-log-success')">Successful reckons</a></li>
            <li><a class="routerlinks" @click="sideNavbarNavigate('reckon-log-fail')">Failed reckons</a></li>
        </ul>
<!--        <ul id="slide-out" class="sidenav">-->
<!--            <li><div class="user-view">-->
<!--                <div class="background">-->
<!--                    <img src="images/office.jpg">-->
<!--                </div>-->
<!--                <a href="#user"><img class="circle" src="images/yuna.jpg"></a>-->
<!--                <a href="#name"><span class="white-text name">John Doe</span></a>-->
<!--                <a href="#email"><span class="white-text email">jdandturk@gmail.com</span></a>-->
<!--            </div></li>-->
<!--            <li><a href="#!"><i class="material-icons">cloud</i>First Link With Icon</a></li>-->
<!--            <li><a href="#!">Second Link</a></li>-->
<!--            <li><div class="divider"></div></li>-->
<!--            <li><a class="subheader">Subheader</a></li>-->
<!--            <li><a class="waves-effect" href="#!">Third Link With Waves</a></li>-->
<!--        </ul>-->
<!--        <a href="#" data-target="slide-out" class="sidenav-trigger"><i class="material-icons">menu</i></a>-->
    </nav>

</template>

<script>

    // import { auth } from '../sensitivedata/firebase';

    export default {
        name: "navbar",
        created() {
            // if (auth.currentUser) {
            //     this.isLogged = true;
            //     this.userEmail = auth.currentUser.email;
            // }
        },
        mounted() {
            M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'));
            this.sideBarInstance = M.Sidenav.init(document.querySelectorAll('.sidenav'));
        },
        data() {
            return {
                isLogged: false,
                userEmail: '',
                sideBarInstance: ''

            }
        },
        methods: {
            // logout: function () {
            //     auth.signOut().then(() => {
            //         this.$router.go({path: this.$router.path});
            //     })
            // },
            sideNavbarNavigate: function (dest) {
                var elem = document.querySelector('.sidenav');
                var instance = M.Sidenav.getInstance(elem);
                instance.close();
                setTimeout(() => {
                    this.$router.push({path: dest});
                }, 200)
            }
        }
    }
</script>

<style scoped>

    #dropdown1 {
        width: 200px !important;
        color: black;
    }

    #dropdown1 .routerlinks{
        color: black;
    }

    nav ul a{
        text-decoration: none !important;
        opacity: 0.7;
        color: white;
        transition: all 0.2s ease-out;
    }

    nav ul a:hover {
        color: white !important;
        opacity: 1;
    }

    .sidenav li > a {
        text-decoration: none !important;
        opacity: 0.7;
        color: white;
        transition: all 0.2s ease-out;
    }

    .navbar-custom {
        background: rgba(99, 202, 193, 1) !important;
        text-color: white !important;
        box-shadow: 5px 5px 10px rgba(0, 0, 0, .25)
    }

    nav .brand-logo {
        position: relative !important;
    }

    .username {
        margin-right: 10px;
    }

    .routerlinks {
        text-decoration: none !important;
        opacity: 0.7;
        color: white;
        transition: all 0.2s ease-out;
    }

    .routerlinks:hover {
        color: white !important;
        opacity: 1;
    }

    @media only screen and (max-width: 600px) {
        .extramargin {
            margin-left: 20px;
            margin-right: 20px;
        }
    }

</style>