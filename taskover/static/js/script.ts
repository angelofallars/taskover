type Task = {
  id: number;
  order: number;
  title: string;
  body: string;
  isCompleted: number;
}

let tasks: Task[] = [];

const addTaskInit = document.querySelector(".add-task-init") as HTMLElement;
const addTaskButton = document.querySelector(".form__add-task") as HTMLElement;
const cancelAddTask = document.querySelector(".form__cancel") as HTMLElement;

// Fetch JSON list of tasks for the user from the API
function fetchTasks(): void {
  const xhttp = new XMLHttpRequest;

  xhttp.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      tasks = JSON.parse(xhttp.responseText);      
      updateTaskView(tasks);
    }
  };

  xhttp.open("GET", "/tasks");
  xhttp.send();
}

function showAddTask() {
  const form = document.querySelector(".form--create"); 
  if (form === null) return;

  form.classList.remove("hidden");
  addTaskInit.classList.add("hidden");
}

function hideAddTask() {
  const form = document.querySelector(".form--create");
  if (form === null) return;

  const title = form.querySelector(".form__title") as HTMLInputElement;
  const body = form.querySelector(".form__body") as HTMLTextAreaElement;
  title.value = "";
  body.value = "";

  addTaskInit.classList.remove("hidden");
  form.classList.add("hidden");
}

// Update the DOM list of tasks
function updateTaskView(newTasks: Task[]): void {
  const taskList = document.querySelector(".task-list") as HTMLElement;

  // Clear the current task list
  while (taskList.lastElementChild) {
    taskList.removeChild(taskList.lastElementChild);
  }

  // Populate the task list with tasks
  newTasks.forEach((task) => {
    const taskElement = document.createElement("div");
    const taskCheckmark = document.createElement("div");
    const taskContent = document.createElement("div");
    const taskContentTitle = document.createElement("div");
    const taskContentBody = document.createElement("div");
    const taskActions = document.createElement("div");

    const taskCheckmarkSymbol = document.createElement("i");
    const taskActionsDelete = document.createElement("i");
    const taskActionsEdit = document.createElement("i");

    taskElement.classList.add("task");
    taskCheckmark.classList.add("task__checkmark");
    taskContent.classList.add("task__content");
    taskContentTitle.classList.add("task__content__title");
    taskContentBody.classList.add("task__content__body");
    taskActions.classList.add("task__actions");

    if (task.isCompleted) {
      taskElement.classList.add("task--completed");
      taskCheckmarkSymbol.classList.add("fas");
      taskCheckmarkSymbol.classList.add("fa-check-circle");
    } else {
      taskCheckmarkSymbol.classList.add("far");
      taskCheckmarkSymbol.classList.add("fa-circle");
    }

    // Mark a task as done / not done
    taskCheckmarkSymbol.addEventListener("click", () => {
      const xhttp = new XMLHttpRequest;

      xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
          fetchTasks();
        }
      };

      xhttp.open("POST", "/mark_completion");
      xhttp.setRequestHeader('Content-Type', 
                             'application/x-www-form-urlencoded');
      xhttp.send(`id=${encodeURIComponent(task.id)}`);
    }); 

    // Delete a task
    taskActionsDelete.addEventListener("click", () => {
      const xhttp = new XMLHttpRequest;

      xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200) {
          fetchTasks();
        }
      };

      xhttp.open("POST", "/delete");
      xhttp.setRequestHeader('Content-Type', 
                             'application/x-www-form-urlencoded');
      xhttp.send(`id=${encodeURIComponent(task.id)}`);
    });

    // Update a task
    taskActionsEdit.addEventListener("click", () => {
      taskElement.classList.add("task--hidden");

      const formUpdate = document.querySelector(".form--update")?.cloneNode(true) as HTMLElement;
      const formTitle = formUpdate.querySelector(".form__title") as HTMLInputElement;
      const formBody = formUpdate.querySelector(".form__body") as HTMLTextAreaElement;

      if (formTitle === null || formBody === null) return;

      formTitle.setAttribute("placeholder", task.title);
      formBody.setAttribute("placeholder", task.body);

      formUpdate.querySelector(".form__add-task")
        ?.addEventListener("click", () => {
          let title = formTitle.value;
          let body = formBody.value;

          if (!title) title = task.title;
          if (!body) body = task.body;

          taskElement.classList.remove("task--hidden");
          taskList.removeChild(formUpdate);

          const xhttp = new XMLHttpRequest();

          xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200) {
              fetchTasks();
            }
          };

          xhttp.open("POST", "/update");
          xhttp.setRequestHeader('Content-Type', 
                                 'application/x-www-form-urlencoded');
          xhttp.send(`title=${encodeURIComponent(title)}
                     &body=${encodeURIComponent(body)}
                     &id=${encodeURIComponent(task.id)}`);
        });

      formUpdate.querySelector(".form__cancel")
        ?.addEventListener("click", () => {
          taskElement.classList.remove("task--hidden");
          taskList.removeChild(formUpdate);
        })

      if (formUpdate === undefined) return;

      formUpdate.classList.remove("hidden");

      taskList.insertBefore(formUpdate, taskElement);
    });

    taskContentTitle.textContent = task.title;
    taskContentBody.textContent = task.body;

    taskActionsDelete.setAttribute("class", "fas fa-trash-alt");
    taskActionsEdit.setAttribute("class", "fas fa-edit");

    taskCheckmark.appendChild(taskCheckmarkSymbol);
    taskContent.appendChild(taskContentTitle);
    taskContent.appendChild(taskContentBody);
    taskActions.appendChild(taskActionsEdit);
    taskActions.appendChild(taskActionsDelete);

    taskElement.appendChild(taskCheckmark);
    taskElement.appendChild(taskContent);
    taskElement.appendChild(taskActions);

    taskList.appendChild(taskElement);
  });
}

// Create task
addTaskButton.addEventListener("click", (e) => {
  const form = document.querySelector(".form--create"); 
  if (form === null) return;

  const title = form.querySelector(".form__title") as HTMLInputElement;
  const body = form.querySelector(".form__body") as HTMLTextAreaElement;
  const titleText = title.value;
  const bodyText = body.value;

  if (!titleText) {
    alert("Title cannot be blank");
    return;
  }


  const xhttp = new XMLHttpRequest;

  xhttp.onreadystatechange = function() {
    if (this.readyState === 4 && this.status === 200) {
      fetchTasks();
      title.value = "";
      body.value = "";
      hideAddTask();
    }
  };

  xhttp.open("POST", "/create");
  xhttp.setRequestHeader('Content-Type', 
                         'application/x-www-form-urlencoded');
  xhttp.send(`title=${encodeURIComponent(titleText)}&body=${encodeURIComponent(bodyText)}`);
});

addTaskInit.addEventListener("click",showAddTask);

cancelAddTask.addEventListener("click", hideAddTask);

fetchTasks();
