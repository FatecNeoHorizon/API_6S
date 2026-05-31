import { apiClient } from "@/api/client"

export const deleteUserRequest = async (userId) => {
  return apiClient.delete(`/users/${userId}`)
}

export const deactivateUserRequest = async (userId) => {
  return apiClient.patch(`/users/${userId}/active`, { active: false })
}
