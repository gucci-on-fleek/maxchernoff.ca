class Animal {
    is_animal = Symbol("Animal")
}
class Dog extends Animal {
    is_dog = Symbol("Dog")
}
class Cat extends Animal {
    is_cat = Symbol("Cat")
}
class Bird extends Animal {
    is_bird = Symbol("Bird")
}

function random_animal(): Dog | Cat {
    return Math.random() < 0.5 ? new Dog() : new Cat()
}

function test_class() {
    const cat_1 = assert_is(new Cat(), Cat) // typeof cat_1 === Cat
    const dog_1 = assert_is(new Dog(), Dog) // typeof dog_1 === Dog
    const bird_1 = assert_is(new Bird(), Bird) // typeof bird_1 === Bird

    const cat_2 = assert_is(new Cat(), Animal) // typeof cat_2 === Animal
    const dog_2 = assert_is(random_animal(), Animal) // typeof dog_2 === Animal
    const dog_3 = assert_is(random_animal(), Dog) // typeof dog_3 === Dog

    const cat_3 = assert_is(new Animal(), Cat) // typeof cat_3 === Cat

    const bird_2 = assert_is(random_animal(), Bird) // Type error!

    console.log("Done!", cat_1, dog_1, bird_1, cat_2, dog_2, dog_3, bird_2)
}

function random_element(): HTMLFormElement | HTMLTemplateElement | null {
    switch (Math.floor(Math.random() * 3)) {
        case 0: return document.createElement("form")
        case 1: return document.createElement("template")
        case 2: return null
    }
    return null
}

function test_element() {
    const form_1 = assert_is(document.createElement("form"), HTMLFormElement) // typeof form_1 === HTMLFormElement
    const template_1 = assert_is(document.createElement("template"), HTMLTemplateElement) // typeof template_1 === HTMLTemplateElement
    const table_1 = assert_is(document.createElement("table"), HTMLTableElement) // typeof table_1 === HTMLTableElement

    const form_2 = assert_is(document.createElement("form"), HTMLElement) // typeof form_2 === HTMLElement
    const template_2 = assert_is(random_element(), HTMLElement) // typeof template_2 === HTMLElement
    const template_3 = assert_is(random_element(), HTMLTemplateElement) // typeof template_3 === HTMLTemplateElement

    const table_2 = assert_is(random_element(), HTMLTableElement) // Type error!

    console.log("Done!", form_1, template_1, table_1, form_2, template_2, template_3, table_2)
}

type Constructor<T> = new (...args: any[]) => T

function assert_is<Value, Target>(
    value: (Value & Target) extends Extract<Value, Target> ? Value : (Target extends Value ? Value : never),
    constructor: Constructor<Target>
): Value extends Target ? Target : (Target extends Value ? Target : never) {
    if (!(value instanceof constructor)) {
        throw new Error(`Expected ${constructor.name}, got ${value?.constructor.name ?? value}`)
    }
    return value as (Value extends Target ? Target : never)
}
type t = typeof assert_is
