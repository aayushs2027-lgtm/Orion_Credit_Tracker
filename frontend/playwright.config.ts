import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'e2e',workers:1,use:{baseURL:'http://127.0.0.1:8000',headless:true,viewport:{width:1536,height:1000}},reporter:'list',timeout:90000});
