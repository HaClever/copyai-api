// Pass the Webdriver Test.
Object.defineProperty(navigator, 'webdriver', {
    get: () => false,
});

// Pass the Chrome Test.
window.navigator.chrome = {
    runtime: {},
};

// Overwrite the `plugins` property to use a custom getter.
Object.defineProperty(navigator, "plugins", {
    get: () => new Array(Math.floor(Math.random() * 6) + 1),
});

// Pass the Permissions Test.

const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
    Promise.resolve({ state: Notification.permission }) :
    originalQuery(parameters)
);