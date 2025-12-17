import { writable } from "svelte/store";
import type { User } from "$lib/types";

export const UserStore = writable<User>({});