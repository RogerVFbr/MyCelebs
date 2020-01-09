import Vue from 'vue'
import Router from 'vue-router'
// import Update from './views/UpdateContact.vue';
// import LoginRegister from './views/LoginRegister.vue';
// import Log from './views/Log.vue';
import ReckonLog from './views/ReckonLog.vue';
import ReckonFailLog from './views/ReckonFailLog.vue';
import RegisterLog from './views/RegisterLog.vue';
import Users from './views/Users.vue';
import Reckon from './views/Reckon.vue';

// import { auth } from './sensitivedata/firebase';

Vue.use(Router)

let router = new Router({
    routes: [
        {
            path: '/',
            name: 'users',
            component: Users

        },
        // {
        //     path: '/log',
        //     name: 'log',
        //     component: Log
        // },
        // {
        //     path: '/add',
        //     name: 'add',
        //     component: () => import('./views/NewContact.vue'),
        //     meta: {
        //         requiresAuth: true
        //     }
        // },
        // {
        //     path: '/update/:item/:itemkey',
        //     name: 'update',
        //     component: Update,
        //     meta: {
        //         requiresAuth: true
        //     }
        // },
        // {
        //     path: '/login',
        //     name: 'login',
        //     component: LoginRegister
        // },
        {
            path: '/reckon-log-success',
            name: 'reckon-log-success',
            component: ReckonLog
        },
        {
            path: '/reckon-log-fail',
            name: 'reckon-log-fail',
            component: ReckonFailLog
        },
        {
            path: '/register-log',
            name: 'register-log',
            component: RegisterLog
        },
        {
            path: '/users',
            name: 'users',
            component: Users
        },
        {
            path: '/reckon',
            name: 'reckon',
            component: Reckon
        },
    ]
})

// router.beforeEach((to, from, next) => {
//     const currentUser = auth.currentUser;
//     const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
//     if (requiresAuth && !currentUser) {
//         next('contacts');
//     }
//     else if (!requiresAuth && currentUser) {
//         next();
//     }
//     else {
//         next();
//     }
// });

export default router;
