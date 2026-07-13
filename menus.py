# -*- coding: utf-8 -*-
"""
Datos de menús de los 3 restaurantes reales usados en la app de demostración
para el semestral de Seguridad en el Desarrollo de Software.
"""

MENUS = {
    "club-de-golf": {
        "slug": "club-de-golf",
        "nombre": "Club de Golf",
        "eslogan": "Menú",
        "contacto": "",
        "telefono": "6893-4599",
        "secciones": [
            {
                "titulo": "Menús",
                "platos": [
                    {
                        "nombre": "Menú Nº1",
                        "descripcion": "Sancocho, arroz blanco, tajada",
                        "precio": 5.50,
                    },
                    {
                        "nombre": "Menú Nº2",
                        "descripcion": "Espagueti de costilla de cerdo",
                        "precio": 6.50,
                    },
                    {
                        "nombre": "Menú Nº3",
                        "descripcion": "Arroz con pollo, lechona, ensalada de papa, plátano en tentación",
                        "precio": 8.00,
                    },
                    {
                        "nombre": "Menú Nº4",
                        "descripcion": "Arroz blanco, filete de corvina al ajillo, ensalada verde y plátano en tentación",
                        "precio": 8.50,
                    },
                ],
            }
        ],
    },
    "el-azteca": {
        "slug": "el-azteca",
        "nombre": "El Azteca",
        "eslogan": "Sabor importado desde México",
        "contacto": "",
        "telefono": "6233-4803",
        "secciones": [
            {
                "titulo": "Entradas",
                "platos": [
                    {"nombre": "Nachos Azteca", "descripcion": "Nachos bañados con queso amarillo y carne asada del Azteca", "precio": 6.50},
                    {"nombre": "Volcanes", "descripcion": "Tostadas de maíz con queso gratinado, carne y cebolla", "precio": 5.50},
                    {"nombre": "Queso Fundido", "descripcion": "Al estilo mexicano para preparar tacos", "precio": 9.00},
                ],
            },
            {
                "titulo": "Especialidades",
                "platos": [
                    {"nombre": "Súper Discada para Compartir", "descripcion": "2 a 3 personas, incluye 12 tortillas para hacer tacos", "precio": 26.00},
                    {"nombre": "Discada Gratinada", "descripcion": "2 a 3 personas, incluye 12 tortillas para hacer tacos", "precio": 28.00},
                    {"nombre": "Orden de Carne Asada", "descripcion": "Acompañada de cebolla asada, chorizo y quesadilla", "precio": 10.00},
                ],
            },
            {
                "titulo": "Tacos",
                "platos": [
                    {"nombre": "(4) Tacos del Azteca con queso", "descripcion": "Tacos de carne asada (tortilla maíz o harina)", "precio": 8.00},
                    {"nombre": "(4) Tacos del Azteca sin queso", "descripcion": "Tacos de carne asada (tortilla maíz o harina)", "precio": 9.00},
                    {"nombre": "(4) Tacos de Pollo Sultán con queso", "descripcion": "Deliciosos tacos hechos con el famoso pollo de la Sultana del Norte", "precio": 8.00},
                    {"nombre": "(4) Tacos de Pollo Sultán sin queso", "descripcion": "Deliciosos tacos hechos con el famoso pollo de la Sultana del Norte", "precio": 9.00},
                    {"nombre": "Pirata (Burrito)", "descripcion": "Taco gigante en tortilla de harina con carne asada y queso", "precio": 9.00},
                    {"nombre": "(4) Tacos de Discada Norteña con queso", "descripcion": "Mezcla de carnes y chorizos, asados en el disco de rastra de campo", "precio": 8.00},
                    {"nombre": "(4) Tacos de Trompo", "descripcion": "Estilo Monterrey, carne de cerdo marinada", "precio": 9.00},
                    {"nombre": "(4) Tacos Mixtos", "descripcion": "Orden mixta de carne asada, pollo sultán, discada norteña y chilorio con queso", "precio": 9.00},
                    {"nombre": "(4) Tacos de Chilorio", "descripcion": "Carne de cerdo preparada con una salsa de chiles no picantes y queso estilo Sinaloa", "precio": 9.00},
                ],
            },
            {
                "titulo": "Niños",
                "platos": [
                    {"nombre": "(3) Quesadillas Norteñas", "descripcion": "", "precio": 5.00},
                ],
            },
            {
                "titulo": "Bebidas",
                "platos": [
                    {"nombre": "Horchata", "descripcion": "", "precio": 3.00},
                    {"nombre": "Soda", "descripcion": "", "precio": 2.00},
                    {"nombre": "Agua", "descripcion": "", "precio": 1.50},
                ],
            },
            {
                "titulo": "Extras",
                "platos": [
                    {"nombre": "Taco individual con queso", "descripcion": "", "precio": 2.50},
                    {"nombre": "Taco individual", "descripcion": "", "precio": 2.00},
                    {"nombre": "Orden de tortillas", "descripcion": "", "precio": 2.00},
                ],
            },
        ],
    },
    "la-frankeria": {
        "slug": "la-frankeria",
        "nombre": "La Frankería",
        "eslogan": "Hamburguesas, burritos, nachos y más",
        "contacto": "",
        "telefono": "0000-0000",
        "secciones": [
            {
                "titulo": "Hamburguesas de Carne",
                "platos": [
                    {"nombre": "Cuarto de Libra con Queso + papas fritas", "descripcion": "", "precio": 5.00},
                    {"nombre": "Classic Cheese Burger + papas fritas", "descripcion": "Nuestra hamburguesa clásica con una capa extra de queso", "precio": 6.50},
                    {"nombre": "Bacon Ranch + papas fritas", "descripcion": "Hamburguesa de carne de 6oz con queso, bacon y ranch", "precio": 7.50},
                    {"nombre": "La Bochinchosa + papas fritas", "descripcion": "Hamburguesa de carne de 6oz con doble de todo", "precio": 7.50},
                    {"nombre": "Mozzarella BBQ + papas fritas", "descripcion": "Hamburguesa de carne de 6oz con mozzarella y BBQ", "precio": 7.50},
                    {"nombre": "Americana Bacon Cheese + papas fritas", "descripcion": "La nueva Americana Bacon Cheese", "precio": 8.50},
                    {"nombre": "La Fogosa + papas fritas", "descripcion": "Hamburguesa de carne de 6oz picante", "precio": 7.75},
                    {"nombre": "La Darks + papas fritas", "descripcion": "Hamburguesa de carne de 6oz doble", "precio": 9.00},
                    {"nombre": "La Yeyesita + papas fritas", "descripcion": "Hamburguesa de carne de 6oz", "precio": 9.50},
                    {"nombre": "El Jefe + papas fritas", "descripcion": "Hamburguesa de carne de 6oz", "precio": 9.50},
                    {"nombre": "La Pocotona + papas fritas", "descripcion": "Hamburguesa de carne de 6oz doble", "precio": 9.50},
                    {"nombre": "Miss Chacalita + papas fritas", "descripcion": "Hamburguesa de carne de 6oz con chorizo", "precio": 10.00},
                    {"nombre": "Manso Pay + papas fritas", "descripcion": "Hamburguesa con una deliciosa combinación", "precio": 10.00},
                    {"nombre": "Super Burra + papas fritas", "descripcion": "Regresa nuestra famosa hamburguesa", "precio": 15.00},
                ],
            },
            {
                "titulo": "Hamburguesas de Pollo",
                "platos": [
                    {"nombre": "Pollo Classic + papas fritas", "descripcion": "Hamburguesa de filete de pollo a la plancha", "precio": 6.50},
                    {"nombre": "Pollo V.I.P. + papas fritas", "descripcion": "Hamburguesa de filete de pollo a la plancha", "precio": 7.00},
                    {"nombre": "Pollo Bacon Sweet + papas fritas", "descripcion": "Hamburguesa de filete de pechuga a la plancha", "precio": 7.50},
                    {"nombre": "Chicken Kardashian + papas fritas", "descripcion": "Hamburguesa de doble filete de pollo", "precio": 12.00},
                    {"nombre": "Chicken Much Hot + papas fritas", "descripcion": "Hamburguesa de doble filete de pollo", "precio": 11.75},
                ],
            },
            {
                "titulo": "Burritos",
                "platos": [
                    {"nombre": "Burrito de Carne + papas fritas", "descripcion": "Tortilla de harina rellena de carne molida", "precio": 6.75},
                    {"nombre": "Burrito de Pollo + papas fritas", "descripcion": "Tortilla de harina rellena de filete de pollo", "precio": 7.00},
                    {"nombre": "Mix Time Burrito + papas fritas", "descripcion": "Tortilla de harina rellena con un mix", "precio": 10.00},
                    {"nombre": "Big Time Burrito + papas fritas", "descripcion": "Tortilla de harina rellena de carne molida", "precio": 11.50},
                    {"nombre": "Gordito Burrito de Carne + papas fritas", "descripcion": "Tortilla de harina de 11\" rellena", "precio": 8.25},
                    {"nombre": "Gordito Burrito de Pollo + papas fritas", "descripcion": "Tortilla de harina de 11\" rellena", "precio": 8.50},
                ],
            },
            {
                "titulo": "Wraps de Pollo",
                "platos": [
                    {"nombre": "Wrap de Pollo Ranch + papas fritas", "descripcion": "Tortilla de harina de 11\" rellena", "precio": 8.00},
                    {"nombre": "Wrap de Pollo Bacon Sweet + papas fritas", "descripcion": "Tortilla de harina de 11\" rellena", "precio": 9.00},
                    {"nombre": "Bazooka Wrap + papas fritas", "descripcion": "Tortilla de harina de 11\" rellena", "precio": 10.50},
                ],
            },
            {
                "titulo": "Nachos",
                "platos": [
                    {"nombre": "Jr. Nachos de Carne", "descripcion": "Porción personal de nachos", "precio": 4.75},
                    {"nombre": "Nachos de Carne", "descripcion": "Tortillas fritas de maíz bañadas en queso", "precio": 6.75},
                    {"nombre": "Cheezy Nachos de Carne", "descripcion": "Tortillas fritas de maíz bañadas en queso", "precio": 8.75},
                    {"nombre": "Cheezy Nachos de Pollo", "descripcion": "Tortillas fritas de maíz bañadas en queso", "precio": 10.00},
                    {"nombre": "Mix Nachos", "descripcion": "Combinación de carne molida y pollo", "precio": 10.00},
                    {"nombre": "Nachos Pa la Dieta", "descripcion": "Extra tortillas fritas de maíz bañadas", "precio": 11.50},
                ],
            },
            {
                "titulo": "Franky Papas",
                "platos": [
                    {"nombre": "Franky Papas de Queso", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 3.75},
                    {"nombre": "Franky Papas con Bacon", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 6.75},
                    {"nombre": "Franky Papas con Carne", "descripcion": "Papas fritas bañadas en carne molida", "precio": 6.75},
                    {"nombre": "Franky Papas de Pollo", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 6.75},
                    {"nombre": "Franky Papas Supreme", "descripcion": "Papas fritas bañadas en carne molida", "precio": 8.00},
                    {"nombre": "Franky Papas Mixtas", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 11.50},
                    {"nombre": "Franky Papas Originales", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 8.00},
                    {"nombre": "Franky Papas Honey", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 8.00},
                    {"nombre": "Franky Papas Buffalo", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 8.00},
                    {"nombre": "Franky Papas Garlic Mayo", "descripcion": "Papas fritas bañadas en queso cheddar", "precio": 8.00},
                ],
            },
            {
                "titulo": "Pollo",
                "platos": [
                    {"nombre": "Chicken Pops + papas fritas", "descripcion": "Orden de popcorn chicken (7oz)", "precio": 6.75},
                    {"nombre": "Chiky Pops + papas fritas", "descripcion": "Popcorn chicken para los chiquitos", "precio": 4.75},
                ],
            },
            {
                "titulo": "Refrescos",
                "platos": [
                    {"nombre": "Pepsi", "descripcion": "", "precio": 1.25},
                    {"nombre": "Ginger Ale", "descripcion": "", "precio": 1.25},
                    {"nombre": "Squirt", "descripcion": "", "precio": 1.25},
                    {"nombre": "Naranja", "descripcion": "", "precio": 1.25},
                    {"nombre": "Botella de Agua", "descripcion": "", "precio": 1.25},
                ],
            },
        ],
    },
}
