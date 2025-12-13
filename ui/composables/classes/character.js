import { faker } from '@faker-js/faker'

export class Character {
    constructor(
        avatar = faker.image.avatar(),
        sex = faker.person.sexType(),
        firstName = faker.person.firstName({ sex }),
        lastName = faker.person.lastName(),
    ) {
        const adjectives = []
        const numOfAdjectives = Math.floor(Math.random() * 5) + 1

        for (let i = 0; i < numOfAdjectives; i++) {
            adjectives.push(faker.word.adjective())
        }

        this.id = faker.string.uuid()
        this.createdAt = new Date()
        this.updatedAt = new Date()
        this.tags = adjectives
        this.avatar = avatar
        this.firstName = firstName
        this.lastName = lastName
        this.sex = sex
    }

    updateAttribute(attribute, value) {
        if (attribute === 'id') {
            throw new Error('Cannot update id')
        }
        this[attribute] = value
        this.updatedAt = new Date() // auto-update timestamp
    }

    clone() {
        const cloned = new Character(
            this.avatar,
            this.sex,
            this.firstName,
            this.lastName,
        )
        cloned.id = faker.string.uuid() // new ID for clone
        cloned.tags = [...this.tags]
        cloned.createdAt = new Date()
        cloned.updatedAt = new Date()
        return cloned
    }

    get name() {
        return `${this.firstName} ${this.lastName}`
    }

    set name(value) {
        const parts = value.split(' ')
        this.firstName = parts[0] || ''
        this.lastName = parts.slice(1).join(' ') || ''
        this.updatedAt = new Date()
    }

    toString() {
        return this.name
    }
}

export default function createRandomCharacter(numOfCharacters = 1) {
    const characters = []

    for (let i = 0; i < numOfCharacters; i++) {
        characters.push(new Character())
    }

    return characters
}
