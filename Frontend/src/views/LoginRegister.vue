<template>
    <div class="add-contacts-container">
        <div id="login" class="center_div login-div-layout">
            <form>
                <div class="form-group">
                    <label for="inputEmail">Type your e-mail:</label>
                    <input type="email"
                           class="form-control cred-input fillDivWidth"
                           id="inputEmail"
                           aria-describedby="inputEmail"
                           placeholder="Enter email"
                           v-model="email">
                    <label for="inputPassword">Type your e-mail:</label>
                    <input type="password"
                           class="form-control cred-input fillDivWidth"
                           id="inputPassword"
                           aria-describedby="inputPassword"
                           placeholder="Enter password"
                           v-model="password">
                </div>
                <button id="loginBtn" type="submit" class="btn btn-primary fillDivWidth"
                        v-on:click="login" v-if="!loggingIn && !signingUp">Login</button>
                <button id="registerBtn" type="submit" class="btn btn-warning fillDivWidth"
                        v-on:click="register" v-if="!loggingIn && !signingUp">Register</button>
                <div class="alert alert-primary fillDivWidth login-register-message" role="alert"
                     v-if="loggingIn">
                    <font-awesome-icon icon="spinner" spin />  Logging in ...
                </div>
                <div class="alert alert-primary fillDivWidth login-register-message" role="alert"
                     v-if="signingUp">
                    <font-awesome-icon icon="spinner" spin />  Signing up ...
                </div>
            </form>
        </div>
    </div>
</template>

<script>

    import { auth } from '../sensitivedata/firebase';

    export default {
        name: "login-register",
        data() {
            return {
                email: '',
                password: '',
                loggingIn: false,
                signingUp: false
            }
        },
        methods: {
            login: function () {
                this.loggingIn = true;
                auth.signInWithEmailAndPassword(this.email, this.password)
                    .then( (user) => {
                        console.log('Successfully logged in.');
                        this.$router.push('/');
                    })
                    .catch( (err) => {
                        this.loggingIn = false;
                        console.log(err);
                        alert('Could not sign in to account. ' + err);
                    });
            },
            register: function () {
                this.signingUp = true;
                auth.createUserWithEmailAndPassword(this.email, this.password)
                    .then(user => {
                        this.signingUp = false;
                        console.log(`Account created for: ${this.email}`);
                        this.login();

                    }, err => {
                        alert('Could not create account. ' + err);
                    });
            }
        }
    }
</script>

<style scoped>
    .add-contacts-container {
        margin-top: 50px;
        padding-bottom: 30px;
    }

    #login {
        width: 230px;
        padding: 20px;
    }

    .fillDivWidth {
        width: 100%;
    }

    .center_div{
        margin: 0 auto;
    }

    .cred-input{
        text-align: center;
        margin-bottom: 20px;
        width: 100%;
    }

    .login-div-layout {
        border: 1px solid rgba(0,0,0,.3);
        border-radius: 5px;
        background: rgba(250,250,250,0.8);
        box-shadow: 5px 5px 30px rgba(0, 0, 0, .4)
    }

    #loginBtn {
        margin-top: 10px;
        margin-bottom: 10px;
    }

    .login-register-message {
        margin-bottom: 0px;
    }
</style>